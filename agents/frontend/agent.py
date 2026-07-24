"""Frontend engineering specialist."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class FrontendAgent(SpecialistAgent):
    name = "frontend"
    domain = AgentDomain.SOFTWARE
    purpose = "Plan user-facing flows, state, accessibility, and UI integration."
    capabilities = ("frontend.design", "state.modeling", "accessibility.review")

    def _handlers(self):
        return {
            **super()._handlers(),
            "plan_frontend_change": self._plan_frontend_change,
            "review_frontend_code": self._review_frontend_code,
        }

    def _plan_frontend_change(self, command: AgentCommand) -> AgentWorkProduct:
        flow = str(command.payload.get("flow", "user flow"))
        return AgentWorkProduct(
            summary="Frontend implementation plan prepared.",
            artifacts=(
                artifact(
                    "implementation_plan",
                    "frontend_plan",
                    (
                        f"Flow: {flow}",
                        "Define screen states before styling.",
                        "Keep controls discoverable and keyboard-accessible.",
                        "Render loading, empty, success, and error states.",
                        "Add view-level tests for the primary workflow.",
                    ),
                ),
            ),
        )

    def _review_frontend_code(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary="Frontend review checklist prepared.",
            artifacts=(
                artifact(
                    "checklist",
                    "frontend_review_checklist",
                    (
                        "No unescaped user content is rendered as HTML.",
                        "State transitions are predictable.",
                        "Long text and RTL strings fit their containers.",
                        "Primary controls have clear disabled and error states.",
                    ),
                ),
            ),
        )
