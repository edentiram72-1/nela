"""Factories for registering the first-wave NELA multi-agent system."""

from __future__ import annotations

from pathlib import Path

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
from agents.security import (
    AnomalyDiscoveryAgent,
    AuthorizedLabAgent,
    CyberDefenseAgent,
    IdentityAccessAgent,
    NetworkDefenseAgent,
    NetworkIntelligenceAgent,
    SecretsHygieneAgent,
    SecureCodeReviewerAgent,
    SupplyChainSecurityAgent,
    VulnerabilityResearchAgent,
)
from agents.test_qa import TestQAAgent
from agents.automation import (
    AppAutomationAgent,
    AutomationAgent,
    AutomationWorkflowAgent,
    ComputerControlAgent,
    FileAutomationAgent,
    ProcessAutomationAgent,
    SchedulerAutomationAgent,
)
from agents.terminal import TerminalAgent
from agents.tryhackme import TryHackMeLearningAgent
from language.learning_store import LearnedResponseStore
from memory.learning_core import LearningMemoryStore


def build_default_agents(
    learning_store_path: Path | str | None = None,
    learning_store: LearnedResponseStore | None = None,
    learning_memory_path: Path | str | None = None,
    learning_memory: LearningMemoryStore | None = None,
):
    """Instantiate the defensive multi-agent foundation in stable registry order."""

    response_store = learning_store or LearnedResponseStore(learning_store_path)
    lesson_store = learning_memory or LearningMemoryStore(learning_memory_path)
    return (
        OrchestratorAgent(),
        PlannerAgent(),
        MemoryAgent(),
        LearningAgent(store=response_store),
        TryHackMeLearningAgent(store=lesson_store),
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
        CyberDefenseAgent(),
        SecretsHygieneAgent(),
        IdentityAccessAgent(),
        NetworkDefenseAgent(),
        NetworkIntelligenceAgent(),
        SupplyChainSecurityAgent(),
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
        AutomationWorkflowAgent(),
        ComputerControlAgent(),
        AppAutomationAgent(),
        FileAutomationAgent(),
        ProcessAutomationAgent(),
        SchedulerAutomationAgent(),
    )


def build_default_registry(
    learning_store_path: Path | str | None = None,
    learning_store: LearnedResponseStore | None = None,
    learning_memory_path: Path | str | None = None,
    learning_memory: LearningMemoryStore | None = None,
) -> AgentRegistry:
    registry = AgentRegistry()
    for agent in build_default_agents(
        learning_store_path=learning_store_path,
        learning_store=learning_store,
        learning_memory_path=learning_memory_path,
        learning_memory=learning_memory,
    ):
        registry.register(agent)
    return registry
