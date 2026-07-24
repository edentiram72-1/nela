"""Factories for registering the first-wave NELA multi-agent system."""

from __future__ import annotations

from agents.backend import BackendAgent
from agents.code_architect import CodeArchitectAgent
from agents.frontend import FrontendAgent
from agents.learning import LearningAgent
from agents.memory import MemoryAgent
from agents.orchestrator import OrchestratorAgent
from agents.planner import PlannerAgent
from agents.registry import AgentRegistry
from agents.security import AnomalyDiscoveryAgent, SecureCodeReviewerAgent, VulnerabilityResearchAgent
from agents.test_qa import TestQAAgent


def build_default_agents():
    """Instantiate the defensive multi-agent foundation in stable registry order."""

    return (
        OrchestratorAgent(),
        PlannerAgent(),
        MemoryAgent(),
        LearningAgent(),
        CodeArchitectAgent(),
        BackendAgent(),
        FrontendAgent(),
        TestQAAgent(),
        SecureCodeReviewerAgent(),
        VulnerabilityResearchAgent(),
        AnomalyDiscoveryAgent(),
    )


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    for agent in build_default_agents():
        registry.register(agent)
    return registry
