"""Automation agent module."""

from agents.automation.agent import AutomationAgent
from agents.automation.computer import (
    AppAutomationAgent,
    AutomationWorkflowAgent,
    ComputerControlAgent,
    FileAutomationAgent,
    ProcessAutomationAgent,
    SchedulerAutomationAgent,
)

__all__ = [
    "AppAutomationAgent",
    "AutomationAgent",
    "AutomationWorkflowAgent",
    "ComputerControlAgent",
    "FileAutomationAgent",
    "ProcessAutomationAgent",
    "SchedulerAutomationAgent",
]
