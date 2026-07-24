"""Backend engineering specialist."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class BackendAgent(SpecialistAgent):
    name = "backend"
    domain = AgentDomain.SOFTWARE
    purpose = "Plan backend changes, APIs, data boundaries, and service behavior."
    capabilities = ("backend.design", "api.contracts", "data.validation")

    def _handlers(self):
        return {
            **super()._handlers(),
            "plan_backend_change": self._plan_backend_change,
            "review_backend_code": self._review_backend_code,
        }

    def _plan_backend_change(self, command: AgentCommand) -> AgentWorkProduct:
        feature = str(command.payload.get("feature", "backend feature"))
        lines = (
            f"Feature: {feature}",
            "Define request and response contracts.",
            "Validate inputs at the boundary.",
            "Keep persistence behind a small adapter.",
            "Add unit tests before wiring external integrations.",
        )
        return AgentWorkProduct(
            summary="Backend implementation plan prepared.",
            artifacts=(artifact("implementation_plan", "backend_plan", lines),),
        )

    def _review_backend_code(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary="Backend code review checklist prepared.",
            artifacts=(
                artifact(
                    "checklist",
                    "backend_review_checklist",
                    (
                        "Input validation is explicit.",
                        "Errors do not leak secrets.",
                        "Database or file writes are scoped.",
                        "Tests cover success, failure, and permission boundaries.",
                    ),
                ),
            ),
        )
