"""Agent dispatcher for event-driven task delegation."""

from __future__ import annotations

import logging
import time

from agents.base import AgentCommand, AgentResult, AgentState, BaseAgent
from agents.registry import AgentRegistry
from brain.planner import Task
from core.events import Event, EventBus, EventTypes
from permissions import AuthenticatedUser, PermissionEngine, PermissionRequest


class AgentDispatcher:
    """Delegates tasks to registered Agents while publishing lifecycle events."""

    def __init__(
        self,
        events: EventBus,
        registry: AgentRegistry | None = None,
        permission_engine: PermissionEngine | None = None,
        authenticated_user: AuthenticatedUser | None = None,
    ) -> None:
        self.events = events
        self.registry = registry or AgentRegistry()
        self.permission_engine = permission_engine or PermissionEngine(events=events)
        self.authenticated_user = authenticated_user or self.permission_engine.default_user
        self.cancelled_tasks: set[str] = set()
        self.logger = logging.getLogger("nela.agents")

    def register_agent(self, agent: BaseAgent) -> None:
        self.registry.register(agent)
        self.permission_engine.register_agent(agent)
        self.events.publish(
            Event(
                type=EventTypes.AGENT_STATUS_CHANGED,
                source="brain.dispatcher",
                payload={"agent": agent.name, "status": agent.status().value},
            )
        )

    def unregister_agent(self, name: str) -> bool:
        removed = self.registry.unregister(name)
        if removed:
            self.permission_engine.unregister_agent(name)
            self.events.publish(
                Event(
                    type=EventTypes.AGENT_STATUS_CHANGED,
                    source="brain.dispatcher",
                    payload={"agent": name, "status": "unregistered"},
                )
            )
        return removed

    def discover_agents(self) -> tuple[str, ...]:
        return self.registry.names()

    def health_check(self) -> dict[str, AgentResult]:
        return self.registry.health_check()

    def cancel_task(self, task_id: str) -> None:
        self.cancelled_tasks.add(task_id)
        self.events.publish(
            Event(
                type=EventTypes.TASK_CANCELLED,
                source="brain.dispatcher",
                payload={"task_id": task_id},
            )
        )

    def dispatch(self, task: Task, plan_id: str) -> AgentResult:
        if task.id in self.cancelled_tasks:
            return self._cancelled(task, plan_id)

        if not task.target_agent:
            return self._agent_unavailable(task, plan_id, "Task has no target agent.")

        agent = self.registry.get(task.target_agent)
        if not agent:
            return self._agent_unavailable(task, plan_id, f"Agent '{task.target_agent}' is not registered.")

        permission_request = PermissionRequest(
            agent=task.target_agent,
            action=task.action,
            payload=task.payload,
            task_id=task.id,
            plan_id=plan_id,
            user=self.authenticated_user,
            confirmed=bool(task.payload.get("confirmed", False)),
            scoped_session_id=_optional_string(task.payload.get("scoped_session_id")),
        )
        permission = self.permission_engine.authorize(permission_request)
        if not permission.granted:
            return self._permission_denied(task, plan_id, permission.reason, permission.to_dict())

        self.events.publish(
            Event(
                type=EventTypes.TASK_DISPATCHED,
                source="brain.dispatcher",
                payload={"plan_id": plan_id, "task_id": task.id, "agent": task.target_agent},
            )
        )

        if agent.status() in {AgentState.CREATED, AgentState.STOPPED}:
            agent.initialize()

        attempts = 0
        last_result = AgentResult(False, "Task was not executed.")
        while attempts < task.retry_policy.max_attempts:
            attempts += 1
            if task.id in self.cancelled_tasks:
                return self._cancelled(task, plan_id)

            self.events.publish(
                Event(
                    type=EventTypes.TASK_STARTED,
                    source="brain.dispatcher",
                    payload={"plan_id": plan_id, "task_id": task.id, "attempt": attempts},
                )
            )

            attempt_started_at = time.monotonic()
            command = AgentCommand(
                action=task.action,
                payload={
                    **task.payload,
                    "task_id": task.id,
                    "plan_id": plan_id,
                    "timeout_seconds": task.timeout_seconds,
                },
                id=permission_request.command_id,
            )
            try:
                last_result = agent.execute(command)
            except Exception as error:  # Defensive boundary for all current and future Agents.
                elapsed = time.monotonic() - attempt_started_at
                last_result = AgentResult(
                    False,
                    f"Agent '{task.target_agent}' raised {error.__class__.__name__}.",
                    {
                        "task_id": task.id,
                        "plan_id": plan_id,
                        "agent": task.target_agent,
                        "error_type": error.__class__.__name__,
                        "error": str(error),
                        "elapsed_seconds": elapsed,
                    },
                )
                self.logger.exception("agent_execute_failed task_id=%s agent=%s", task.id, task.target_agent)
                break
            elapsed = time.monotonic() - attempt_started_at
            timed_out = task.timeout_seconds is not None and elapsed > task.timeout_seconds
            if timed_out and not last_result.success:
                last_result = AgentResult(False, "Task timed out.", {"elapsed_seconds": elapsed})
            elif timed_out:
                last_result = AgentResult(
                    True,
                    last_result.message,
                    {
                        **last_result.data,
                        "elapsed_seconds": elapsed,
                        "timeout_exceeded": True,
                    },
                )

            if last_result.success:
                self.permission_engine.record_action_result(permission_request, last_result, permission)
                self.events.publish(
                    Event(
                        type=EventTypes.TASK_COMPLETED,
                        source="brain.dispatcher",
                        payload={
                            "plan_id": plan_id,
                            "task_id": task.id,
                            "agent": task.target_agent,
                            "attempts": attempts,
                            "elapsed_seconds": elapsed,
                        },
                    )
                )
                return last_result

            if attempts < task.retry_policy.max_attempts and task.retry_policy.backoff_seconds:
                time.sleep(task.retry_policy.backoff_seconds)

        self.logger.error("task_failed task_id=%s agent=%s", task.id, task.target_agent)
        self.permission_engine.record_action_result(permission_request, last_result, permission)
        self.events.publish(
            Event(
                type=EventTypes.TASK_FAILED,
                source="brain.dispatcher",
                payload={
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "agent": task.target_agent,
                    "message": last_result.message,
                    "attempts": attempts,
                },
            )
        )
        return last_result

    def _agent_unavailable(self, task: Task, plan_id: str, message: str) -> AgentResult:
        result = AgentResult(False, message, {"task_id": task.id, "plan_id": plan_id})
        self.events.publish(
            Event(
                type=EventTypes.AGENT_UNAVAILABLE,
                source="brain.dispatcher",
                payload={
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "agent": task.target_agent,
                    "message": message,
                },
            )
        )
        return result

    def _permission_denied(self, task: Task, plan_id: str, message: str, details: dict[str, object]) -> AgentResult:
        result = AgentResult(False, message, {"task_id": task.id, "plan_id": plan_id, **details})
        if details.get("decision") == "confirmation_required":
            return result
        self.events.publish(
            Event(
                type=EventTypes.TASK_FAILED,
                source="brain.dispatcher",
                payload={
                    "plan_id": plan_id,
                    "task_id": task.id,
                    "agent": task.target_agent,
                    "message": message,
                    "permission": details,
                },
            )
        )
        return result

    def _cancelled(self, task: Task, plan_id: str) -> AgentResult:
        result = AgentResult(False, "Task was cancelled.", {"task_id": task.id, "plan_id": plan_id})
        self.events.publish(
            Event(
                type=EventTypes.TASK_CANCELLED,
                source="brain.dispatcher",
                payload={"plan_id": plan_id, "task_id": task.id},
            )
        )
        return result


def _optional_string(value: object) -> str | None:
    return str(value) if value else None
