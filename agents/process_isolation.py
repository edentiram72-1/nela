"""Subprocess isolation boundary for blocking or high-risk Agent work."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import multiprocessing
import time
from typing import Any, Callable


class ProcessOutcome(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"
    CRASHED = "crashed"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProcessExecutionResult:
    success: bool
    message: str
    timed_out: bool = False
    exit_code: int | None = None
    data: dict[str, Any] = field(default_factory=dict)
    outcome: ProcessOutcome = ProcessOutcome.UNKNOWN


class IsolatedAgentProcessRunner:
    """Runs blocking work in a child process that can be terminated."""

    def __init__(
        self,
        timeout_seconds: float,
        before_terminate: Callable[[], None] | None = None,
        cancel_check: Callable[[], bool] | None = None,
        on_start: Callable[[int], None] | None = None,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.before_terminate = before_terminate
        self.cancel_check = cancel_check
        self.on_start = on_start

    def run(self, target: Callable[..., Any], *args: Any, **kwargs: Any) -> ProcessExecutionResult:
        queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=1)
        process = multiprocessing.Process(target=_worker, args=(queue, target, args, kwargs))
        process.start()
        if self.on_start is not None and process.pid is not None:
            self.on_start(process.pid)

        deadline = time.monotonic() + self.timeout_seconds
        cancelled = False
        while process.is_alive():
            if self.cancel_check is not None and self.cancel_check():
                cancelled = True
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            process.join(min(0.05, remaining))

        if process.is_alive():
            if self.before_terminate is not None:
                self.before_terminate()
            process.terminate()
            process.join(1.0)
            if process.is_alive():
                process.kill()
                process.join(1.0)
            return ProcessExecutionResult(
                False,
                "Isolated Agent process was cancelled and terminated."
                if cancelled
                else "Isolated Agent process timed out and was terminated.",
                timed_out=not cancelled,
                exit_code=process.exitcode,
                outcome=ProcessOutcome.CANCELLED if cancelled else ProcessOutcome.TIMED_OUT,
            )

        if queue.empty():
            return ProcessExecutionResult(
                False,
                "Isolated Agent process exited without a result.",
                exit_code=process.exitcode,
                outcome=ProcessOutcome.UNKNOWN if process.exitcode == 0 else ProcessOutcome.CRASHED,
            )
        payload = queue.get()
        return ProcessExecutionResult(
            bool(payload["success"]),
            str(payload["message"]),
            exit_code=process.exitcode,
            data=dict(payload.get("data") or {}),
            outcome=ProcessOutcome.COMPLETED if payload["success"] else ProcessOutcome.FAILED,
        )


def _worker(queue: multiprocessing.Queue, target: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
    try:
        result = target(*args, **kwargs)
        queue.put({"success": True, "message": "completed", "data": {"result": result}})
    except Exception as error:
        queue.put(
            {
                "success": False,
                "message": f"{error.__class__.__name__}: {error}",
                "data": {"error_type": error.__class__.__name__, "error": str(error)},
            }
        )


def blocking_sleep(seconds: float) -> str:
    """Test helper kept top-level so multiprocessing can run it."""

    time.sleep(seconds)
    return "done"
