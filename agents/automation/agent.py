"""Computer automation coordinator agent."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct


class AutomationAgent(SpecialistAgent):
    name = "automation"
    domain = AgentDomain.SOFTWARE
    purpose = "Coordinate safe local computer automation workflows across specialist automation agents."
    capabilities = ("automation.workflow", "automation.routing", "automation.runbook")

    def _handlers(self):
        return {
            **super()._handlers(),
            "create_automation_workflow": self._create_automation_workflow,
            "route_computer_task": self._route_computer_task,
        }

    def _create_automation_workflow(self, command: AgentCommand) -> AgentWorkProduct:
        objective = str(command.payload.get("objective", "computer task"))
        steps = tuple(str(step) for step in command.payload.get("steps", ()))
        if not steps:
            steps = (
                "Understand the target application, file, or process.",
                "Preview every action in dry-run mode.",
                "Ask for approval before side effects.",
                "Execute only allowlisted local actions.",
                "Collect evidence and summarize the result.",
            )
        return AgentWorkProduct(
            summary="Automation workflow prepared.",
            steps=steps,
            artifacts=(artifact("runbook", "automation_workflow", (f"Objective: {objective}", *steps)),),
            next_steps=("Dispatch each step to the narrowest automation specialist.",),
        )

    def _route_computer_task(self, command: AgentCommand) -> AgentWorkProduct:
        task_type = str(command.payload.get("task_type", "workflow"))
        routes = {
            "ui": "computer_control",
            "app": "app_automation",
            "file": "file_automation",
            "process": "process_automation",
            "schedule": "scheduler_automation",
            "workflow": "automation_workflow",
        }
        target = routes.get(task_type, "automation_workflow")
        return AgentWorkProduct(
            summary=f"Computer task routed to {target}.",
            artifacts=(artifact("route", "automation_route", (f"task_type={task_type}", f"target_agent={target}")),),
        )
