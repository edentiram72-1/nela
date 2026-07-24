"""Learning and improvement specialist."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class LearningAgent(SpecialistAgent):
    name = "learning"
    domain = AgentDomain.LEARNING
    purpose = "Convert outcomes into reusable lessons and learning paths."
    capabilities = ("lesson.capture", "curriculum.recommendation", "gap.analysis")

    def _handlers(self):
        return {
            **super()._handlers(),
            "record_lesson": self._record_lesson,
            "recommend_learning_plan": self._recommend_learning_plan,
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
