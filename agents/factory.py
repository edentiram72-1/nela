"""Factories for registering the first-wave NELA multi-agent system."""

from __future__ import annotations

from agents.backend import BackendAgent
from agents.browser import BrowserAgent
from agents.code_architect import CodeArchitectAgent
from agents.files import FilesAgent
from agents.frontend import FrontendAgent
from agents.github import GitHubAgent
from agents.learning import LearningAgent
from agents.memory import MemoryAgent
from agents.orchestrator import OrchestratorAgent
from agents.planner import PlannerAgent
from agents.registry import AgentRegistry
from agents.role_agents import (
    BlueTeamAgent,
    CodeReviewerAgent,
    ContainmentAgent,
    DataEngineerAgent,
    DeceptionAgent,
    DetectionEngineeringAgent,
    DevOpsEngineerAgent,
    DocumentationAgent,
    DocumentationResearcherAgent,
    ExploitValidationAgent,
    ForensicsAgent,
    IncidentCommanderAgent,
    InfrastructureSecurityAgent,
    LLMEngineerAgent,
    MLEngineerAgent,
    MobileEngineerAgent,
    PurpleTeamAgent,
    QualitySelfEvaluationAgent,
    RecoveryAgent,
    RedTeamSimulatorAgent,
    ResearchAgent,
    SecurityResearcherAgent,
    SentinelAgent,
    TestEngineerAgent,
    ThreatHunterAgent,
    ThreatIntelligenceAgent,
    TrendMonitorAgent,
)
from agents.security import AnomalyDiscoveryAgent, AuthorizedLabAgent, SecureCodeReviewerAgent, VulnerabilityResearchAgent
from agents.test_qa import TestQAAgent
from agents.automation import AutomationAgent
from agents.terminal import TerminalAgent


def build_default_agents():
    """Instantiate the defensive multi-agent foundation in stable registry order."""

    return (
        OrchestratorAgent(),
        PlannerAgent(),
        MemoryAgent(),
        LearningAgent(),
        QualitySelfEvaluationAgent(),
        CodeArchitectAgent(),
        BackendAgent(),
        FrontendAgent(),
        MobileEngineerAgent(),
        DevOpsEngineerAgent(),
        CodeReviewerAgent(),
        TestQAAgent(),
        TestEngineerAgent(),
        DocumentationAgent(),
        LLMEngineerAgent(),
        MLEngineerAgent(),
        DataEngineerAgent(),
        ResearchAgent(),
        DocumentationResearcherAgent(),
        TrendMonitorAgent(),
        SecurityResearcherAgent(),
        SecureCodeReviewerAgent(),
        VulnerabilityResearchAgent(),
        InfrastructureSecurityAgent(),
        ThreatIntelligenceAgent(),
        SentinelAgent(),
        IncidentCommanderAgent(),
        ContainmentAgent(),
        DeceptionAgent(),
        ForensicsAgent(),
        ThreatHunterAgent(),
        RedTeamSimulatorAgent(),
        BlueTeamAgent(),
        PurpleTeamAgent(),
        ExploitValidationAgent(),
        DetectionEngineeringAgent(),
        RecoveryAgent(),
        AnomalyDiscoveryAgent(),
        AuthorizedLabAgent(),
        BrowserAgent(),
        TerminalAgent(),
        GitHubAgent(),
        FilesAgent(),
        AutomationAgent(),
    )


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    for agent in build_default_agents():
        registry.register(agent)
    return registry
