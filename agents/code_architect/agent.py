"""Software architecture specialist."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class CodeArchitectAgent(SpecialistAgent):
    name = "code_architect"
    domain = AgentDomain.SOFTWARE
    purpose = "Design modular implementation boundaries and review architecture risk."
    capabilities = ("architecture.design", "interface.design", "risk.review")

    def _handlers(self):
        return {
            **super()._handlers(),
            "design_architecture": self._design_architecture,
            "review_architecture": self._review_architecture,
        }

    def _design_architecture(self, command: AgentCommand) -> AgentWorkProduct:
        feature = str(command.payload.get("feature", "new capability"))
        lines = (
            f"Feature: {feature}",
            "Interfaces: define dataclasses for inputs, findings, artifacts, and task output.",
            "Registry: register agents by stable names and expose manifests.",
            "Policy: validate every command before handler execution.",
            "Tests: cover route creation, policy denial, and each specialist action.",
        )
        return AgentWorkProduct(
            summary="Architecture outline prepared.",
            artifacts=(artifact("architecture", "module_boundary_plan", lines),),
        )

    def _review_architecture(self, command: AgentCommand) -> AgentWorkProduct:
        modules = tuple(command.payload.get("modules", ()))
        findings: list[TaskFinding] = []
        if not modules:
            findings.append(
                TaskFinding(
                    "No modules supplied for architecture review.",
                    severity=RiskLevel.LOW,
                    category="architecture",
                    recommendation="Pass the affected module list so ownership and dependencies can be checked.",
                )
            )
        return AgentWorkProduct(
            summary=f"Reviewed {len(modules)} module(s) for architecture shape.",
            findings=tuple(findings),
            next_steps=("Keep cross-agent contracts small and stable.",),
        )
