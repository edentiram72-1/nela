"""Safe local computer automation specialist agents."""

from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Iterable

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskArtifact, TaskFinding


class AutomationWorkflowAgent(SpecialistAgent):
    name = "automation_workflow"
    domain = AgentDomain.SOFTWARE
    purpose = "Turn repeated computer work into reviewable, resumable runbooks."
    capabilities = ("workflow.runbook", "workflow.validation", "workflow.checkpoints")

    def _handlers(self):
        return {**super()._handlers(), "build_runbook": self._build_runbook, "validate_runbook": self._validate_runbook}

    def _build_runbook(self, command: AgentCommand) -> AgentWorkProduct:
        objective = str(command.payload.get("objective", "repeatable computer workflow"))
        steps = tuple(str(step) for step in command.payload.get("steps", ()))
        if not steps:
            steps = (
                "Open or inspect the required local resource.",
                "Preview the intended action.",
                "Check permission tier and required approval.",
                "Run the narrowest safe action.",
                "Verify output and record evidence.",
            )
        return AgentWorkProduct(
            summary="Automation runbook prepared.",
            steps=steps,
            artifacts=(artifact("runbook", "computer_automation_runbook", (f"Objective: {objective}", *steps)),),
        )

    def _validate_runbook(self, command: AgentCommand) -> AgentWorkProduct:
        steps = tuple(str(step) for step in command.payload.get("steps", ()))
        findings = []
        if not steps:
            findings.append(
                TaskFinding(
                    "Runbook has no steps",
                    RiskLevel.MEDIUM,
                    "automation",
                    recommendation="Add explicit preview, approval, execution, and verification steps.",
                )
            )
        if steps and not any("verify" in step.lower() or "check" in step.lower() for step in steps):
            findings.append(
                TaskFinding(
                    "Runbook lacks verification",
                    RiskLevel.LOW,
                    "automation",
                    recommendation="Add a final verification step with observable evidence.",
                )
            )
        return AgentWorkProduct(summary=f"Runbook validation completed for {len(steps)} step(s).", findings=tuple(findings))


class ComputerControlAgent(SpecialistAgent):
    name = "computer_control"
    domain = AgentDomain.SOFTWARE
    purpose = "Prepare keyboard, mouse, and screen interaction plans without direct UI side effects."
    capabilities = ("ui.sequence.plan", "keyboard.plan", "mouse.plan")

    def _handlers(self):
        return {**super()._handlers(), "plan_ui_sequence": self._plan_ui_sequence, "dry_run_ui_sequence": self._dry_run_ui_sequence}

    def _plan_ui_sequence(self, command: AgentCommand) -> AgentWorkProduct:
        application = str(command.payload.get("application", "target application"))
        actions = tuple(str(action) for action in command.payload.get("actions", ()))
        if not actions:
            actions = ("focus application", "inspect current screen", "preview click/type target", "wait for visible confirmation")
        return AgentWorkProduct(
            summary="UI automation sequence prepared.",
            steps=actions,
            artifacts=(artifact("ui_sequence", "computer_control_sequence", (f"Application: {application}", *actions)),),
            next_steps=("Use Computer Use or Desktop Agent only after approval and visual verification.",),
        )

    def _dry_run_ui_sequence(self, command: AgentCommand) -> AgentWorkProduct:
        actions = tuple(str(action) for action in command.payload.get("actions", ()))
        return AgentWorkProduct(
            summary=f"Dry-run UI sequence contains {len(actions)} action(s).",
            steps=actions,
            artifacts=(artifact("dry_run", "ui_dry_run", actions or ("No UI actions supplied.",)),),
        )


class AppAutomationAgent(SpecialistAgent):
    name = "app_automation"
    domain = AgentDomain.SOFTWARE
    purpose = "Plan safe local application lifecycle and handoff actions."
    capabilities = ("app.workflow", "app.lifecycle.plan", "app.handoff")

    def _handlers(self):
        return {**super()._handlers(), "plan_app_workflow": self._plan_app_workflow}

    def _plan_app_workflow(self, command: AgentCommand) -> AgentWorkProduct:
        application = str(command.payload.get("application", "application"))
        return AgentWorkProduct(
            summary="Application automation plan prepared.",
            steps=(
                f"Resolve application: {application}",
                "Check whether the app is allowlisted for Desktop Agent control.",
                "Preview launch/focus/close action.",
                "Require confirmation for close or destructive app actions.",
                "Verify app state after execution.",
            ),
            artifacts=(artifact("app_plan", "app_automation_plan", (f"Application: {application}", "Use DesktopAgent for real lifecycle control.")),),
        )


class FileAutomationAgent(SpecialistAgent):
    name = "file_automation"
    domain = AgentDomain.SOFTWARE
    purpose = "Preview local file organization, copy, move, and cleanup tasks inside approved roots."
    capabilities = ("file.workflow", "file.preview", "file.scope")

    def _handlers(self):
        return {**super()._handlers(), "preview_file_operation": self._preview_file_operation}

    def _preview_file_operation(self, command: AgentCommand) -> AgentWorkProduct:
        operation = str(command.payload.get("operation", "inspect"))
        paths = tuple(str(path) for path in command.payload.get("paths", ()))
        findings = []
        for path in paths:
            if ".." in Path(path).parts:
                findings.append(
                    TaskFinding(
                        "Path traversal marker in file operation preview",
                        RiskLevel.HIGH,
                        "file_automation",
                        location=path,
                        recommendation="Canonicalize and approve the target root before any file action.",
                    )
                )
        return AgentWorkProduct(
            summary=f"File operation preview prepared: {operation}.",
            findings=tuple(findings),
            artifacts=(artifact("file_preview", "file_operation_preview", (f"operation={operation}", *paths)),),
            next_steps=("Use a scoped file agent or explicit code edit path for real file changes.",),
        )


class ProcessAutomationAgent(SpecialistAgent):
    name = "process_automation"
    domain = AgentDomain.SOFTWARE
    purpose = "Preview and run a tiny allowlist of local verification commands without shell access."
    capabilities = ("process.preview", "process.allowlisted_run", "process.evidence")

    def _handlers(self):
        return {
            **super()._handlers(),
            "preview_process_run": self._preview_process_run,
            "run_allowlisted_command": self._run_allowlisted_command,
        }

    def _preview_process_run(self, command: AgentCommand) -> AgentWorkProduct:
        argv = _argv_from_payload(command.payload)
        return AgentWorkProduct(
            summary="Process run preview prepared.",
            artifacts=(artifact("command_preview", "process_command", (_format_command(argv),)),),
            next_steps=("Run only if the command is allowlisted and approval is explicit.",),
        )

    def _run_allowlisted_command(self, command: AgentCommand) -> AgentWorkProduct:
        argv = _argv_from_payload(command.payload)
        dry_run = bool(command.payload.get("dry_run", True))
        approved = bool(command.payload.get("approved", False))
        if tuple(argv) not in ALLOWLISTED_COMMANDS:
            return _blocked_process_product("Command is not allowlisted.", argv)
        if dry_run:
            return AgentWorkProduct(
                summary="Dry-run command accepted; nothing executed.",
                artifacts=(artifact("command_preview", "allowlisted_command_dry_run", (_format_command(argv),)),),
            )
        if not approved:
            return _blocked_process_product("Approved flag is required before command execution.", argv)

        cwd = _safe_cwd(command.payload)
        completed = subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True, timeout=30, check=False)
        return AgentWorkProduct(
            summary=f"Allowlisted command finished with exit code {completed.returncode}.",
            artifacts=(
                TaskArtifact("stdout", "command_stdout", completed.stdout[-4000:]),
                TaskArtifact("stderr", "command_stderr", completed.stderr[-4000:]),
                artifact("command", "executed_command", (_format_command(argv), f"cwd={cwd}", f"returncode={completed.returncode}")),
            ),
            findings=(
                ()
                if completed.returncode == 0
                else (
                    TaskFinding(
                        "Allowlisted command returned non-zero exit code",
                        RiskLevel.MEDIUM,
                        "process_automation",
                        evidence=str(completed.returncode),
                        recommendation="Inspect stderr/stdout and fix the failing local check.",
                    ),
                )
            ),
        )


class SchedulerAutomationAgent(SpecialistAgent):
    name = "scheduler_automation"
    domain = AgentDomain.SOFTWARE
    purpose = "Design local recurring task plans without installing timers by default."
    capabilities = ("schedule.plan", "schedule.validation", "recurrence.preview")

    def _handlers(self):
        return {**super()._handlers(), "plan_scheduled_task": self._plan_scheduled_task}

    def _plan_scheduled_task(self, command: AgentCommand) -> AgentWorkProduct:
        task = str(command.payload.get("task", "automation task"))
        recurrence = str(command.payload.get("recurrence", "manual"))
        return AgentWorkProduct(
            summary="Scheduled automation plan prepared.",
            steps=(
                f"Task: {task}",
                f"Recurrence: {recurrence}",
                "Keep first run manual and dry-run.",
                "Require approval before installing a persistent schedule.",
                "Write audit evidence for each run.",
            ),
            artifacts=(artifact("schedule_plan", "scheduled_task_plan", (f"task={task}", f"recurrence={recurrence}")),),
        )


ALLOWLISTED_COMMANDS: frozenset[tuple[str, ...]] = frozenset(
    {
        ("python3", "-m", "unittest", "discover", "-s", "tests"),
        ("python3", "-m", "scripts.validate_language_packs"),
        ("python3", "-m", "ui.app", "--headless-smoke"),
        ("git", "status", "--short", "--branch"),
    }
)


def _argv_from_payload(payload: dict[str, object]) -> tuple[str, ...]:
    command = payload.get("command", ())
    if isinstance(command, str):
        return tuple(part for part in command.split(" ") if part)
    if isinstance(command, Iterable):
        return tuple(str(part) for part in command)
    return ()


def _format_command(argv: tuple[str, ...]) -> str:
    return " ".join(argv) if argv else "<empty command>"


def _safe_cwd(payload: dict[str, object]) -> Path:
    requested = Path(str(payload.get("cwd", Path.cwd()))).expanduser().resolve()
    allowed_root = Path(str(payload.get("allowed_root", Path.cwd()))).expanduser().resolve()
    if requested == allowed_root or allowed_root in requested.parents:
        return requested
    return allowed_root


def _blocked_process_product(reason: str, argv: tuple[str, ...]) -> AgentWorkProduct:
    return AgentWorkProduct(
        summary=f"Process automation blocked: {reason}",
        findings=(
            TaskFinding(
                "Process run blocked",
                RiskLevel.HIGH,
                "process_automation",
                evidence=_format_command(argv),
                recommendation="Use an allowlisted command, dry-run first, and provide approval for execution.",
            ),
        ),
    )
