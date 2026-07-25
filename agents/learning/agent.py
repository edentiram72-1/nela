"""Learning and improvement specialist."""

from __future__ import annotations

from pathlib import Path

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct
from language.learning_store import LearnedResponseStore


class LearningAgent(SpecialistAgent):
    name = "learning"
    domain = AgentDomain.LEARNING
    purpose = "Convert outcomes, phrases, and user-taught responses into reusable learning assets."
    capabilities = ("lesson.capture", "curriculum.recommendation", "gap.analysis", "language.learning")

    def __init__(self, store: LearnedResponseStore | None = None, store_path: Path | str | None = None) -> None:
        super().__init__()
        self.store = store or LearnedResponseStore(store_path)

    def _handlers(self):
        return {
            **super()._handlers(),
            "record_lesson": self._record_lesson,
            "recommend_learning_plan": self._recommend_learning_plan,
            "teach_response": self._teach_response,
            "list_learned_responses": self._list_learned_responses,
        }

    def _record_lesson(self, command: AgentCommand) -> AgentWorkProduct:
        lesson = str(command.payload.get("lesson", "No lesson supplied.")).strip()
        tags = tuple(command.payload.get("tags", ()))
        return AgentWorkProduct(
            summary="Lesson prepared for memory storage.",
            artifacts=(artifact("lesson", "learning_lesson", (lesson, f"Tags: {', '.join(tags) if tags else 'none'}")),),
            next_steps=("Store the lesson through the memory agent after user/project approval.",),
        )

    def _recommend_learning_plan(self, command: AgentCommand) -> AgentWorkProduct:
        topic = str(command.payload.get("topic", "secure software engineering"))
        lines = (
            f"Topic: {topic}",
            "1. Read current project code and docs.",
            "2. Build a small local exercise.",
            "3. Add tests that prove the behavior.",
            "4. Review the result for security and maintainability.",
            "5. Capture one reusable lesson.",
        )
        return AgentWorkProduct(
            summary="Learning plan prepared.",
            artifacts=(artifact("learning_plan", "learning_path", lines),),
        )

    def _teach_response(self, command: AgentCommand) -> AgentWorkProduct:
        trigger = str(command.payload.get("trigger", "")).strip()
        response = str(command.payload.get("response", "")).strip()
        tags = tuple(str(item) for item in command.payload.get("tags", ("conversation", "hebrew")))
        learned = self.store.add_response(trigger=trigger, response=response, tags=tags)
        return AgentWorkProduct(
            summary="Learned response stored for future conversations.",
            artifacts=(
                artifact(
                    "learned_response",
                    learned.id,
                    (
                        f"trigger={learned.trigger}",
                        f"response={learned.response}",
                        f"tags={', '.join(learned.tags) if learned.tags else 'none'}",
                    ),
                ),
            ),
            next_steps=("Ask the trigger phrase in the next conversation turn to verify the response.",),
        )

    def _list_learned_responses(self, command: AgentCommand) -> AgentWorkProduct:
        responses = self.store.list_responses()
        lines = tuple(f"{item.trigger} => {item.response}" for item in responses) or ("No learned responses yet.",)
        return AgentWorkProduct(
            summary=f"Found {len(responses)} learned response(s).",
            artifacts=(artifact("learned_responses", "language_memory", lines),),
        )
