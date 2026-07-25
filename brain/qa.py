"""Conversation QA layer for safe NELA self-knowledge."""

from __future__ import annotations

from dataclasses import dataclass

from brain.context import ContextSnapshot
from brain.dispatcher import AgentDispatcher
from brain.intent_router import Intent
from brain.memory_manager import MemoryManager


CONVERSATIONAL_ACTIONS = frozenset(
    {
        "Greeting",
        "Thanks",
        "IdentityQuestion",
        "CapabilitiesQuestion",
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

    def answer(
        self,
        intent: Intent,
        dispatcher: AgentDispatcher,
        context: ContextSnapshot,
        memory: MemoryManager,
    ) -> KnowledgeAnswer:
        agents = dispatcher.discover_agents()
        health = dispatcher.health_check()
        healthy_count = sum(1 for result in health.values() if result.success)
        agent_list = _agent_list(agents)
        variables: dict[str, object] = {
            "agent_count": len(agents),
            "healthy_count": healthy_count,
            "agents": agent_list,
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
        if intent.action == "AgentStatusQuestion":
            return KnowledgeAnswer("qa.agent_status", "agent_status", variables)
        return KnowledgeAnswer("qa.unknown", "unknown", variables)


def _agent_list(agents: tuple[str, ...], limit: int = 12) -> str:
    visible = tuple(sorted(agents))[:limit]
    suffix = "" if len(agents) <= limit else f" ועוד {len(agents) - limit}"
    return ", ".join(visible) + suffix
