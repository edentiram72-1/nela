"""Subprocess isolation boundary for blocking or high-risk Agent work."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import multiprocessing
import threading
import time
from typing import Any, Callable
from uuid import uuid4


class ProcessOutcome(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"
    TIMED_OUT = "timed_out"
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
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self.before_terminate = before_terminate
        self._process: multiprocessing.Process | None = None
        self._termination_requested = False
        self._lock = threading.Lock()

    def run(self, target: Callable[..., Any], *args: Any, **kwargs: Any) -> ProcessExecutionResult:
        queue: multiprocessing.Queue = multiprocessing.Queue(maxsize=1)
        process = multiprocessing.Process(target=_worker, args=(queue, target, args, kwargs))
        process.start()
        with self._lock:
            self._process = process
            terminate_now = self._termination_requested
        if terminate_now:
            self._terminate_process(process)
            result = self._terminated_result(process)
            self._clear_process(process)
            return result

        process.join(self.timeout_seconds)
        with self._lock:
            was_terminated = self._termination_requested
        if process.is_alive():
            self.terminate()
            result = self._timeout_result(process)
            self._clear_process(process)
            return result

        self._clear_process(process)
        if was_terminated:
            return self._terminated_result(process)
        if queue.empty():
            return ProcessExecutionResult(
                process.exitcode == 0,
                "Isolated Agent process exited without a result.",
                exit_code=process.exitcode,
                outcome=ProcessOutcome.UNKNOWN,
            )
        payload = queue.get()
        return ProcessExecutionResult(
            bool(payload["success"]),
            str(payload["message"]),
            exit_code=process.exitcode,
            data=dict(payload.get("data") or {}),
            outcome=ProcessOutcome.COMPLETED if payload["success"] else ProcessOutcome.FAILED,
        )

    def terminate(self) -> bool:
        """Request termination of the currently running isolated process."""

        with self._lock:
            self._termination_requested = True
            process = self._process
        if process is None:
            return True
        return self._terminate_process(process)

    def _terminate_process(self, process: multiprocessing.Process) -> bool:
        if not process.is_alive():
            return False
        if self.before_terminate is not None:
            self.before_terminate()
        process.terminate()
        process.join(1.0)
        if process.is_alive():
            process.kill()
            process.join(1.0)
        return True

    def _clear_process(self, process: multiprocessing.Process) -> None:
        with self._lock:
            if self._process is process:
                self._process = None

    def _timeout_result(self, process: multiprocessing.Process) -> ProcessExecutionResult:
        return ProcessExecutionResult(
            False,
            "Isolated Agent process timed out and was terminated.",
            timed_out=True,
            exit_code=process.exitcode,
            outcome=ProcessOutcome.TIMED_OUT,
        )

    def _terminated_result(self, process: multiprocessing.Process) -> ProcessExecutionResult:
        return ProcessExecutionResult(
            False,
            "Isolated Agent process was terminated by the kill switch.",
            exit_code=process.exitcode,
            outcome=ProcessOutcome.TERMINATED,
        )


class IsolatedProcessSupervisor:
    """Tracks live isolated runners so emergency controls can stop them."""

    def __init__(self) -> None:
        self._runners: dict[str, IsolatedAgentProcessRunner] = {}
        self._lock = threading.Lock()

    def register(self, runner: IsolatedAgentProcessRunner) -> str:
        token = str(uuid4())
        with self._lock:
            self._runners[token] = runner
        return token

    def unregister(self, token: str) -> None:
        with self._lock:
            self._runners.pop(token, None)

    def terminate_all(self) -> int:
        with self._lock:
            runners = tuple(self._runners.values())
        terminated = 0
        for runner in runners:
            if runner.terminate():
                terminated += 1
        return terminated

    def active_count(self) -> int:
        with self._lock:
            return len(self._runners)


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
