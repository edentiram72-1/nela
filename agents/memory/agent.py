"""Memory specialist agent."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class MemoryAgent(SpecialistAgent):
    name = "memory"
    domain = AgentDomain.MEMORY
    purpose = "Store and retrieve scoped lessons, project facts, and task summaries."
    capabilities = ("memory.write", "memory.read", "memory.summarize")

    def __init__(self) -> None:
        super().__init__()
        self._items: list[dict[str, object]] = []

    def _handlers(self):
        return {
            **super()._handlers(),
            "remember": self._remember,
            "recall": self._recall,
            "summarize_memory": self._summarize_memory,
        }

    def _remember(self, command: AgentCommand) -> AgentWorkProduct:
        content = str(command.payload.get("content", "")).strip()
        tags = tuple(command.payload.get("tags", ()))
        if content:
            self._items.append({"content": content, "tags": tags})
        return AgentWorkProduct(
            summary="Memory item stored." if content else "No memory content supplied.",
            artifacts=(artifact("memory", "stored_memory", (content or "empty",)),),
        )

    def _recall(self, command: AgentCommand) -> AgentWorkProduct:
        query = str(command.payload.get("query", "")).lower()
        matches = tuple(
            item for item in self._items if not query or query in str(item.get("content", "")).lower()
        )
        lines = tuple(str(item["content"]) for item in matches) or ("No matching memories.",)
        return AgentWorkProduct(
            summary=f"Recalled {len(matches)} memory item(s).",
            artifacts=(artifact("memory", "recall_results", lines),),
        )

    def _summarize_memory(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary=f"Memory contains {len(self._items)} item(s).",
            artifacts=(
                artifact(
                    "summary",
                    "memory_summary",
                    tuple(str(item["content"]) for item in self._items[-5:]) or ("No memories stored.",),
                ),
            ),
        )
