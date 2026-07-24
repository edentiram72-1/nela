"""Testing and quality specialist."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class TestQAAgent(SpecialistAgent):
    name = "test_qa"
    domain = AgentDomain.QUALITY
    purpose = "Define tests, quality gates, and local verification paths."
    capabilities = ("test.strategy", "qa.review", "regression.risk")

    def _handlers(self):
        return {
            **super()._handlers(),
            "create_test_strategy": self._create_test_strategy,
            "review_quality": self._review_quality,
        }

    def _create_test_strategy(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target", "changed behavior"))
        lines = (
            f"Target: {target}",
            "Unit tests for each specialist handler.",
            "Integration tests for registry and dispatcher routing.",
            "Policy tests for denied security requests.",
            "Regression tests for existing public agent contracts.",
        )
        return AgentWorkProduct(
            summary="Test strategy prepared.",
            artifacts=(artifact("test_strategy", "qa_strategy", lines),),
        )

    def _review_quality(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary="Quality review checklist prepared.",
            artifacts=(
                artifact(
                    "checklist",
                    "quality_gate",
                    (
                        "Tests are deterministic and local.",
                        "Failures include actionable messages.",
                        "Security guardrails are asserted, not just documented.",
                        "Docs match the implemented agent names and actions.",
                    ),
                ),
            ),
        )
