"""Multi-agent orchestration specialist."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class OrchestratorAgent(SpecialistAgent):
    name = "orchestrator"
    domain = AgentDomain.ORCHESTRATION
    purpose = "Break goals into safe specialist handoffs and consolidate outcomes."
    capabilities = ("agent.routing", "work.consolidation", "policy.first_coordination")

    def _handlers(self):
        return {
            **super()._handlers(),
            "orchestrate": self._orchestrate,
            "consolidate_results": self._consolidate_results,
        }

    def _orchestrate(self, command: AgentCommand) -> AgentWorkProduct:
        objective = str(command.payload.get("objective", "No objective provided."))
        requested_agents = tuple(command.payload.get("agents", ()))
        agents = requested_agents or (
            "planner",
            "code_architect",
            "backend",
            "frontend",
            "test_qa",
            "secure_code_reviewer",
        )
        steps = tuple(
            f"{index}. {agent}: handle its scoped part of '{objective}'."
            for index, agent in enumerate(agents, start=1)
        )
        return AgentWorkProduct(
            summary="Defensive multi-agent route prepared.",
            artifacts=(artifact("plan", "orchestration_route", steps),),
            next_steps=("Dispatch the plan through the registry and keep policy checks enabled.",),
        )

    def _consolidate_results(self, command: AgentCommand) -> AgentWorkProduct:
        results = command.payload.get("results", ())
        summaries = tuple(str(item.get("summary", item)) if isinstance(item, dict) else str(item) for item in results)
        return AgentWorkProduct(
            summary=f"Consolidated {len(summaries)} agent result(s).",
            artifacts=(artifact("summary", "consolidated_results", summaries or ("No results supplied.",)),),
            next_steps=("Review findings by severity before implementation.",),
        )
