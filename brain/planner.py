"""Task planning for NELA OS."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any
from uuid import uuid4

from brain.intent_router import Intent


class TaskMode(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class TaskStatus(str, Enum):
    PENDING = "pending"
    DISPATCHED = "dispatched"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class RetryPolicy:
    max_attempts: int = 1
    backoff_seconds: float = 0.0


@dataclass(frozen=True)
class Task:
    description: str
    action: str
    capability: str | None = None
    target_agent: str | None = None
    mode: TaskMode = TaskMode.SEQUENTIAL
    depends_on: tuple[str, ...] = ()
    condition: str | None = None
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    timeout_seconds: float | None = 30.0
    payload: dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    id: str = field(default_factory=lambda: str(uuid4()))

    def with_status(self, status: TaskStatus) -> "Task":
        return replace(self, status=status)


@dataclass(frozen=True)
class Plan:
    intent: Intent
    tasks: tuple[Task, ...]
    id: str = field(default_factory=lambda: str(uuid4()))
    cancellable: bool = True

    def pending_tasks(self) -> tuple[Task, ...]:
        return tuple(task for task in self.tasks if task.status == TaskStatus.PENDING)


class Planner:
    """Converts an Intent into executable, agent-neutral Tasks."""

    def create_plan(self, intent: Intent) -> Plan:
        target_agent = intent.target_agent
        tasks: list[Task] = []

        if intent.action == "OpenApplication":
            tasks.append(
                Task(
                    description=f"Request application launch: {intent.application or 'requested application'}",
                    action="launch_application",
                    capability="desktop.application.launch",
                    payload={"application": intent.application},
                    retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1.0),
                    timeout_seconds=20.0,
                )
            )
        elif intent.action == "CloseApplication":
            tasks.append(
                Task(
                    description=f"Request application close: {intent.application or 'requested application'}",
                    action="close_application",
                    capability="desktop.application.close",
                    payload={
                        "application": intent.application,
                        "confirmed": intent.parameters.get("confirmed", False),
                        "confirmation_action_hash": intent.parameters.get("confirmation_action_hash"),
                        "confirmation_expires_at": intent.parameters.get("confirmation_expires_at"),
                    },
                    timeout_seconds=20.0,
                )
            )
        elif intent.action == "SwitchApplication":
            tasks.append(
                Task(
                    description=f"Bring application to foreground: {intent.application or 'requested application'}",
                    action="switch_application",
                    capability="desktop.application.focus",
                    payload={"application": intent.application},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "PlayMedia":
            tasks.extend(self._media_tasks(intent))
        elif intent.action == "Remember":
            tasks.append(
                Task(
                    description="Store user-approved memory",
                    action="remember",
                    capability="memory.write",
                    target_agent="memory",
                    payload={"content": intent.raw_text},
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "TeachResponse":
            tasks.append(
                Task(
                    description="Teach NELA a user-provided response pair",
                    action="teach_response",
                    capability="teach_response",
                    target_agent="learning",
                    payload={
                        "trigger": intent.parameters.get("trigger", ""),
                        "response": intent.parameters.get("response", ""),
                        "tags": ("conversation", "hebrew", "user_taught"),
                    },
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "SecurityReview":
            tasks.append(
                Task(
                    description="Run defensive security review on supplied text or code",
                    action="review_code_security",
                    capability="review_code_security",
                    target_agent="secure_code_reviewer",
                    payload={"source": intent.raw_text, "path": "conversation"},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "ThreatModel":
            tasks.append(
                Task(
                    description="Prepare a defensive threat model",
                    action="threat_model",
                    capability="threat_model",
                    target_agent="secure_code_reviewer",
                    payload={"asset": intent.resource or intent.raw_text},
                    timeout_seconds=10.0,
                )
            )
        elif intent.action == "CyberLabStatus":
            tasks.append(
                Task(
                    description="Read authorized cyber lab status",
                    action="lab_status",
                    capability="lab_status",
                    target_agent="authorized_lab",
                    payload={},
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "CyberLabRegisterTarget":
            tasks.append(
                Task(
                    description="Register a local or owned cyber lab target",
                    action="register_lab_target",
                    capability="register_lab_target",
                    target_agent="authorized_lab",
                    payload={
                        "target": intent.resource or "localhost",
                        "scope_type": "local_lab",
                        "owner": "local-owner",
                        "proof": "declared local or owned lab target from conversation",
                    },
                    timeout_seconds=5.0,
                )
            )
        elif intent.action == "LocalFuzzPlan":
            tasks.append(
                Task(
                    description="Prepare a local-only fuzzing plan",
                    action="create_local_fuzz_plan",
                    capability="create_local_fuzz_plan",
                    target_agent="anomaly_discovery",
                    payload={"target": intent.resource or intent.raw_text},
                    timeout_seconds=10.0,
                )
            )
        else:
            tasks.append(
                Task(
                    description=f"Delegate request: {intent.raw_text}",
                    action=_action_to_command(intent.action),
                    capability=str(intent.parameters.get("capability") or _action_to_command(intent.action)),
                    target_agent=target_agent,
                    payload={
                        "text": intent.raw_text,
                        "application": intent.application,
                        "resource": intent.resource,
                        "confirmed": intent.parameters.get("confirmed", False),
                        "confirmation_action_hash": intent.parameters.get("confirmation_action_hash"),
                        "confirmation_expires_at": intent.parameters.get("confirmation_expires_at"),
                    },
                )
            )

        return Plan(intent=intent, tasks=tuple(tasks))

    def cancel_plan(self, plan: Plan) -> Plan:
        return replace(
            plan,
            tasks=tuple(
                task.with_status(TaskStatus.CANCELLED)
                if task.status in {TaskStatus.PENDING, TaskStatus.DISPATCHED, TaskStatus.RUNNING}
                else task
                for task in plan.tasks
            ),
        )

    def _media_tasks(self, intent: Intent) -> tuple[Task, ...]:
        agent = intent.target_agent
        launch = Task(
            description=f"Ensure application is available: {intent.application or 'media application'}",
            action="ensure_application",
            capability="media.application.prepare" if agent else "desktop.application.launch",
            target_agent=agent or "desktop",
            payload={"application": intent.application},
            retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1.0),
            timeout_seconds=20.0,
        )
        wait = Task(
            description="Wait until the application is ready",
            action="wait_until_ready",
            capability="media.application.status" if agent else "desktop.application.status",
            target_agent=agent or "desktop",
            depends_on=(launch.id,),
            payload={"application": intent.application},
            timeout_seconds=20.0,
        )
        search = Task(
            description="Find requested media resource",
            action="search_media",
            capability="media.search",
            target_agent=agent,
            depends_on=(wait.id,),
            payload={"resource": intent.resource, "text": intent.raw_text},
            timeout_seconds=15.0,
        )
        play = Task(
            description="Start media playback",
            action="play_media",
            capability="media.play",
            target_agent=agent,
            depends_on=(search.id,),
            payload={"resource": intent.resource},
            timeout_seconds=10.0,
        )
        return (launch, wait, search, play)


def _action_to_command(action: str) -> str:
    output = []
    for char in action:
        if char.isupper() and output:
            output.append("_")
        output.append(char.lower())
    return "".join(output)
