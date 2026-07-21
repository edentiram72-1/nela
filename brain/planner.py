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
                    target_agent=target_agent or "desktop",
                    payload={"application": intent.application},
                    retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1.0),
                    timeout_seconds=20.0,
                )
            )
        elif intent.action == "PlayMedia":
            tasks.extend(self._media_tasks(intent))
        elif intent.action == "Remember":
            tasks.append(
                Task(
                    description="Store user-approved memory",
                    action="remember",
                    target_agent="memory",
                    payload={"content": intent.raw_text},
                    timeout_seconds=5.0,
                )
            )
        else:
            tasks.append(
                Task(
                    description=f"Delegate request: {intent.raw_text}",
                    action=_action_to_command(intent.action),
                    target_agent=target_agent,
                    payload={
                        "text": intent.raw_text,
                        "application": intent.application,
                        "resource": intent.resource,
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
            target_agent=agent or "desktop",
            payload={"application": intent.application},
            retry_policy=RetryPolicy(max_attempts=2, backoff_seconds=1.0),
            timeout_seconds=20.0,
        )
        wait = Task(
            description="Wait until the application is ready",
            action="wait_until_ready",
            target_agent=agent or "desktop",
            depends_on=(launch.id,),
            payload={"application": intent.application},
            timeout_seconds=20.0,
        )
        search = Task(
            description="Find requested media resource",
            action="search_media",
            target_agent=agent,
            depends_on=(wait.id,),
            payload={"resource": intent.resource, "text": intent.raw_text},
            timeout_seconds=15.0,
        )
        play = Task(
            description="Start media playback",
            action="play_media",
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
