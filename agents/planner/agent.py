"""Specialist planning agent."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class PlannerAgent(SpecialistAgent):
    name = "planner"
    domain = AgentDomain.PLANNING
    purpose = "Turn broad goals into small, reviewable tasks."
    capabilities = ("task.decomposition", "acceptance.criteria", "dependency.mapping")

    def _handlers(self):
        return {
            **super()._handlers(),
            "create_agent_plan": self._create_agent_plan,
        }

    def _create_agent_plan(self, command: AgentCommand) -> AgentWorkProduct:
        objective = str(command.payload.get("objective", "Build a safe feature increment."))
        constraints = tuple(command.payload.get("constraints", ()))
        lines = (
            f"Goal: {objective}",
            "1. Clarify boundaries and policy constraints.",
            "2. Identify affected modules and ownership.",
            "3. Assign implementation to the narrowest specialist agents.",
            "4. Run quality and defensive security checks.",
            "5. Consolidate results with blockers and next actions.",
        )
        if constraints:
            lines = (*lines, "Constraints:", *(f"- {constraint}" for constraint in constraints))
        return AgentWorkProduct(
            summary="Agent plan created.",
            artifacts=(artifact("plan", "agent_task_plan", lines),),
            next_steps=("Create concrete tasks with target_agent and action fields.",),
        )
