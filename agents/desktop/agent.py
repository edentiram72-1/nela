"""macOS Desktop Agent V1.

This Agent only manages the lifecycle of known macOS applications. It never
executes arbitrary shell text, force-kills processes, modifies files, or asks
for elevated privileges.
"""

from __future__ import annotations

from dataclasses import dataclass
import subprocess
import time
from typing import Protocol

from agents.base import AgentCommand, AgentResult, BaseAgent


@dataclass(frozen=True)
class ApplicationSpec:
    """Known macOS application metadata."""

    canonical_name: str
    bundle_id: str
    process_names: tuple[str, ...]
    aliases: tuple[str, ...]


SUPPORTED_APPLICATIONS: tuple[ApplicationSpec, ...] = (
    ApplicationSpec(
        canonical_name="Google Chrome",
        bundle_id="com.google.Chrome",
        process_names=("Google Chrome",),
        aliases=("chrome", "google chrome"),
    ),
    ApplicationSpec(
        canonical_name="Safari",
        bundle_id="com.apple.Safari",
        process_names=("Safari",),
        aliases=("safari",),
    ),
    ApplicationSpec(
        canonical_name="Finder",
        bundle_id="com.apple.finder",
        process_names=("Finder",),
        aliases=("finder",),
    ),
    ApplicationSpec(
        canonical_name="VS Code",
        bundle_id="com.microsoft.VSCode",
        process_names=("Code", "Visual Studio Code"),
        aliases=("vs code", "vscode", "visual studio code", "code"),
    ),
    ApplicationSpec(
        canonical_name="Terminal",
        bundle_id="com.apple.Terminal",
        process_names=("Terminal",),
        aliases=("terminal",),
    ),
)


class DesktopCommandRunner(Protocol):
    """Small command boundary used to mock macOS calls in tests."""

    def run(self, argv: tuple[str, ...], timeout: float) -> subprocess.CompletedProcess[str]:
        """Run a fixed argv command."""


class SubprocessDesktopCommandRunner:
    """Runs fixed macOS command invocations without a shell."""

    def run(self, argv: tuple[str, ...], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )


class DesktopAgent(BaseAgent):
    """Controls supported macOS applications through safe lifecycle commands."""

    name = "desktop"

    def __init__(
        self,
        runner: DesktopCommandRunner | None = None,
        supported_applications: tuple[ApplicationSpec, ...] = SUPPORTED_APPLICATIONS,
    ) -> None:
        super().__init__()
        self._runner = runner or SubprocessDesktopCommandRunner()
        self._applications = supported_applications

    def execute(self, command: AgentCommand) -> AgentResult:
        started_at = time.monotonic()
        application_name = _application_from_payload(command)
        try:
            if _is_disabled_application(application_name):
                return self._result(
                    success=False,
                    message="פתיחת Spotify כבויה לפי ההעדפה שלך.",
                    action=command.action,
                    application=application_name,
                    started_at=started_at,
                    extra={
                        "disabled_application": True,
                        "supported_applications": self.supported_application_names(),
                    },
                )
            spec = self._resolve_application(application_name)
            if spec is None:
                return self._result(
                    success=False,
                    message=f"Unsupported desktop application: {application_name or 'unknown'}.",
                    action=command.action,
                    application=application_name,
                    started_at=started_at,
                    extra={"supported_applications": self.supported_application_names()},
                )

            if command.action in {"launch_application", "ensure_application"}:
                return self._launch_or_focus(spec, command.action, started_at)
            if command.action in {"bring_to_front", "switch_application", "focus_application"}:
                return self._bring_to_front(spec, command.action, started_at)
            if command.action in {"is_application_running", "detect_application", "status_application"}:
                return self._detect_running(spec, command.action, started_at)
            if command.action == "wait_until_ready":
                return self._wait_until_ready(spec, command, started_at)
            if command.action in {"close_application", "quit_application"}:
                return self._close_application(spec, command.action, started_at)

            return self._result(
                success=False,
                message="Unsupported desktop lifecycle action.",
                action=command.action,
                application=spec.canonical_name,
                started_at=started_at,
                extra={
                    "supported_actions": (
                        "launch_application",
                        "ensure_application",
                        "bring_to_front",
                        "switch_application",
                        "focus_application",
                        "is_application_running",
                        "detect_application",
                        "status_application",
                        "wait_until_ready",
                        "close_application",
                        "quit_application",
                    )
                },
            )
        except subprocess.TimeoutExpired as error:
            return self._timeout_failure(command, application_name, started_at, error)

    def health_check(self) -> AgentResult:
        result = super().health_check()
        return AgentResult(
            result.success,
            result.message,
            {
                **result.data,
                "supported_applications": self.supported_application_names(),
                "safety": "application_lifecycle_only",
            },
        )

    def supported_application_names(self) -> tuple[str, ...]:
        return tuple(spec.canonical_name for spec in self._applications)

    def _launch_or_focus(self, spec: ApplicationSpec, action: str, started_at: float) -> AgentResult:
        was_running = self._is_running(spec)
        command_result = self._open_application(spec)
        if command_result.returncode != 0:
            return self._command_failure(spec, action, started_at, command_result)

        return self._result(
            success=True,
            message=(
                f"{spec.canonical_name} brought to foreground."
                if was_running
                else f"{spec.canonical_name} launch requested."
            ),
            action="bring_to_front" if was_running else "launch",
            application=spec.canonical_name,
            started_at=started_at,
            extra={"already_running": was_running, "bundle_id": spec.bundle_id},
        )

    def _bring_to_front(self, spec: ApplicationSpec, action: str, started_at: float) -> AgentResult:
        if not self._is_running(spec):
            return self._result(
                success=False,
                message=f"{spec.canonical_name} is not running.",
                action=action,
                application=spec.canonical_name,
                started_at=started_at,
                extra={"running": False, "bundle_id": spec.bundle_id},
            )

        command_result = self._open_application(spec)
        if command_result.returncode != 0:
            return self._command_failure(spec, action, started_at, command_result)

        return self._result(
            success=True,
            message=f"{spec.canonical_name} brought to foreground.",
            action="bring_to_front",
            application=spec.canonical_name,
            started_at=started_at,
            extra={"running": True, "bundle_id": spec.bundle_id},
        )

    def _detect_running(self, spec: ApplicationSpec, action: str, started_at: float) -> AgentResult:
        running = self._is_running(spec)
        return self._result(
            success=True,
            message=f"{spec.canonical_name} is {'running' if running else 'not running'}.",
            action="detect_running",
            application=spec.canonical_name,
            started_at=started_at,
            extra={"running": running, "bundle_id": spec.bundle_id},
        )

    def _wait_until_ready(self, spec: ApplicationSpec, command: AgentCommand, started_at: float) -> AgentResult:
        timeout_seconds = float(command.payload.get("timeout_seconds") or 10.0)
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() <= deadline:
            if self._is_running(spec):
                return self._result(
                    success=True,
                    message=f"{spec.canonical_name} is ready.",
                    action="wait_until_ready",
                    application=spec.canonical_name,
                    started_at=started_at,
                    extra={"running": True, "bundle_id": spec.bundle_id},
                )
            time.sleep(0.2)

        return self._result(
            success=False,
            message=f"{spec.canonical_name} did not become ready before timeout.",
            action="wait_until_ready",
            application=spec.canonical_name,
            started_at=started_at,
            extra={"running": False, "bundle_id": spec.bundle_id, "timeout_seconds": timeout_seconds},
        )

    def _close_application(self, spec: ApplicationSpec, action: str, started_at: float) -> AgentResult:
        if not self._is_running(spec):
            return self._result(
                success=True,
                message=f"{spec.canonical_name} is not running.",
                action="close",
                application=spec.canonical_name,
                started_at=started_at,
                extra={"running": False, "already_closed": True, "bundle_id": spec.bundle_id},
            )

        command_result = self._runner.run(
            ("/usr/bin/osascript", "-e", f'tell application id "{spec.bundle_id}" to quit'),
            timeout=10.0,
        )
        if command_result.returncode != 0:
            return self._command_failure(spec, action, started_at, command_result)

        return self._result(
            success=True,
            message=f"{spec.canonical_name} close requested.",
            action="close",
            application=spec.canonical_name,
            started_at=started_at,
            extra={"running": True, "bundle_id": spec.bundle_id},
        )

    def _resolve_application(self, application_name: str | None) -> ApplicationSpec | None:
        if not application_name:
            return None
        normalized = _normalize_application_name(application_name)
        for spec in self._applications:
            names = (_normalize_application_name(spec.canonical_name), *spec.aliases)
            if normalized in names:
                return spec
        return None

    def _is_running(self, spec: ApplicationSpec) -> bool:
        for process_name in spec.process_names:
            result = self._runner.run(("/usr/bin/pgrep", "-x", process_name), timeout=2.0)
            if result.returncode == 0:
                return True
        return False

    def _open_application(self, spec: ApplicationSpec) -> subprocess.CompletedProcess[str]:
        return self._runner.run(("/usr/bin/open", "-b", spec.bundle_id), timeout=10.0)

    def _command_failure(
        self,
        spec: ApplicationSpec,
        action: str,
        started_at: float,
        command_result: subprocess.CompletedProcess[str],
    ) -> AgentResult:
        return self._result(
            success=False,
            message=f"{spec.canonical_name} {action} failed.",
            action=action,
            application=spec.canonical_name,
            started_at=started_at,
            extra={
                "bundle_id": spec.bundle_id,
                "returncode": command_result.returncode,
                "stderr": command_result.stderr.strip(),
            },
        )

    def _timeout_failure(
        self,
        command: AgentCommand,
        application_name: str | None,
        started_at: float,
        error: subprocess.TimeoutExpired,
    ) -> AgentResult:
        return self._result(
            success=False,
            message=f"Desktop command timed out while running {command.action}.",
            action=command.action,
            application=application_name,
            started_at=started_at,
            extra={
                "error": "TimeoutExpired",
                "timeout_seconds": error.timeout,
            },
        )

    def _result(
        self,
        success: bool,
        message: str,
        action: str,
        application: str | None,
        started_at: float,
        extra: dict[str, object] | None = None,
    ) -> AgentResult:
        execution_time_ms = round((time.monotonic() - started_at) * 1000, 3)
        status = "success" if success else "failed"
        return AgentResult(
            success=success,
            message=message,
            data={
                "status": status,
                "application": application,
                "action": action,
                "execution_time_ms": execution_time_ms,
                **(extra or {}),
            },
        )


def _application_from_payload(command: AgentCommand) -> str | None:
    value = command.payload.get("application") or command.payload.get("app")
    return str(value).strip() if value else None


def _is_disabled_application(application_name: str | None) -> bool:
    if not application_name:
        return False
    return _normalize_application_name(application_name) in {"spotify", "ספוטיפיי", "ספוטי"}


def _normalize_application_name(value: str) -> str:
    return " ".join(value.lower().replace(".", "").strip().split())
