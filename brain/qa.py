"""Conversation QA layer for safe NELA self-knowledge."""

from __future__ import annotations

from dataclasses import dataclass

from brain.context import ContextSnapshot
from brain.dispatcher import AgentDispatcher
from brain.intent_router import Intent
from brain.memory_manager import MemoryManager
from language.learning_store import LearnedResponseStore


CONVERSATIONAL_ACTIONS = frozenset(
    {
        "Greeting",
        "Thanks",
        "IdentityQuestion",
        "CapabilitiesQuestion",
        "SecurityCapabilitiesQuestion",
        "HumanStatusQuestion",
        "AgentStatusQuestion",
        "GeneralQuestion",
    }
)


@dataclass(frozen=True)
class KnowledgeAnswer:
    """A semantic answer that the language layer can render."""

    category: str
    message: str
    variables: dict[str, object]


class KnowledgeEngine:
    """Answers safe conversation questions without delegating to external Agents."""

    def __init__(self, learned_responses: LearnedResponseStore | None = None) -> None:
        self.learned_responses = learned_responses or LearnedResponseStore()

    def answer(
        self,
        intent: Intent,
        dispatcher: AgentDispatcher,
        context: ContextSnapshot,
        memory: MemoryManager,
    ) -> KnowledgeAnswer:
        learned = self.learned_responses.find_response(intent.raw_text)
        if learned is not None:
            return KnowledgeAnswer(
                "qa.learned",
                learned.response,
                {
                    "answer": learned.response,
                    "trigger": learned.trigger,
                    "source": learned.source,
                },
            )

        agents = dispatcher.discover_agents()
        health = dispatcher.health_check()
        healthy_count = sum(1 for result in health.values() if result.success)
        agent_list = _agent_list(agents)
        security_agents = _agent_list(tuple(agent for agent in agents if _is_security_agent(agent)), limit=10)
        variables: dict[str, object] = {
            "agent_count": len(agents),
            "healthy_count": healthy_count,
            "agents": agent_list,
            "security_agents": security_agents,
            "last_intent": context.last_intent or "אין עדיין פקודה קודמת",
            "running_tasks": len(context.running_tasks),
            "recent_turns": len(memory.recent_context(limit=5)),
        }

        if intent.action == "Greeting":
            return KnowledgeAnswer("qa.greeting", "greeting", variables)
        if intent.action == "Thanks":
            return KnowledgeAnswer("qa.thanks", "thanks", variables)
        if intent.action == "IdentityQuestion":
            return KnowledgeAnswer("qa.identity", "identity", variables)
        if intent.action == "CapabilitiesQuestion":
            return KnowledgeAnswer("qa.capabilities", "capabilities", variables)
        if intent.action == "SecurityCapabilitiesQuestion":
            return KnowledgeAnswer("qa.security_capabilities", "security_capabilities", variables)
        if intent.action == "HumanStatusQuestion":
            return KnowledgeAnswer("qa.human_status", "human_status", variables)
        if intent.action == "AgentStatusQuestion":
            return KnowledgeAnswer("qa.agent_status", "agent_status", variables)
        return KnowledgeAnswer("qa.unknown", "unknown", variables)


def _agent_list(agents: tuple[str, ...], limit: int = 12) -> str:
    visible = tuple(sorted(agents))[:limit]
    suffix = "" if len(agents) <= limit else f" ועוד {len(agents) - limit}"
    return ", ".join(visible) + suffix


def _is_security_agent(agent: str) -> bool:
    return agent in {
        "cyber_defense",
        "secure_code_reviewer",
        "vulnerability_research",
        "security_researcher",
        "infrastructure_security",
        "threat_intelligence",
        "sentinel",
        "incident_commander",
        "containment",
        "deception",
        "forensics",
        "threat_hunter",
        "red_team_simulator",
        "blue_team",
        "purple_team",
        "exploit_validation",
        "detection_engineering",
        "recovery",
        "anomaly_discovery",
        "authorized_lab",
    }
