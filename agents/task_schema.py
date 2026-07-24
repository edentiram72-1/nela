"""Shared task and result schema for NELA specialist agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class AgentDomain(str, Enum):
    ORCHESTRATION = "orchestration"
    PLANNING = "planning"
    MEMORY = "memory"
    LEARNING = "learning"
    SOFTWARE = "software"
    QUALITY = "quality"
    SECURITY = "security"


class RiskLevel(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class TaskArtifact:
    """A reusable output emitted by an agent."""

    kind: str
    name: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TaskFinding:
    """A structured observation from code, config, dependency, or anomaly review."""

    title: str
    severity: RiskLevel = RiskLevel.INFO
    category: str = "general"
    location: str | None = None
    evidence: str | None = None
    recommendation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity.value,
            "category": self.category,
            "location": self.location,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class AgentTask:
    """Agent-neutral task envelope used by the multi-agent layer."""

    objective: str
    action: str
    domain: AgentDomain
    target_agent: str | None = None
    inputs: dict[str, Any] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: str(uuid4()))


@dataclass(frozen=True)
class AgentWorkProduct:
    """Normalized specialist output for orchestration and tests."""

    summary: str
    findings: tuple[TaskFinding, ...] = ()
    artifacts: tuple[TaskArtifact, ...] = ()
    next_steps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "artifacts": [
                {
                    "kind": artifact.kind,
                    "name": artifact.name,
                    "content": artifact.content,
                    "metadata": artifact.metadata,
                }
                for artifact in self.artifacts
            ],
            "next_steps": list(self.next_steps),
        }
