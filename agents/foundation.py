"""Base implementation for deterministic specialist agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.policy import DefensivePolicyGuard, ToolPermissionProfile, default_tool_permissions
from agents.task_schema import AgentDomain, AgentWorkProduct, TaskArtifact, TaskFinding


@dataclass(frozen=True)
class AgentManifest:
    name: str
    domain: AgentDomain
    purpose: str
    capabilities: tuple[str, ...]
    permission_profile: ToolPermissionProfile

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "domain": self.domain.value,
            "purpose": self.purpose,
            "capabilities": list(self.capabilities),
            "permission_profile": self.permission_profile.to_dict(),
        }


class SpecialistAgent(BaseAgent):
    """Policy-aware base for first-wave NELA multi-agent roles."""

    domain: AgentDomain = AgentDomain.SOFTWARE
    purpose: str = "Specialist agent."
    capabilities: tuple[str, ...] = ()

    def __init__(self, policy: DefensivePolicyGuard | None = None) -> None:
        super().__init__()
        self.policy = policy or DefensivePolicyGuard()

    @property
    def manifest(self) -> AgentManifest:
        permissions = default_tool_permissions()[self.name]
        return AgentManifest(
            name=self.name,
            domain=self.domain,
            purpose=self.purpose,
            capabilities=self.capabilities,
            permission_profile=permissions,
        )

    def execute(self, command: AgentCommand) -> AgentResult:
        policy = self.policy.validate(command.action, command.payload)
        if not policy.allowed:
            return AgentResult(
                False,
                policy.reason,
                {
                    "agent": self.name,
                    "policy_decision": policy.decision.value,
                    "matched_terms": list(policy.matched_terms),
                    "allowed_scope": "defensive_authorized_work_only",
                },
            )

        handler = self._handlers().get(command.action)
        if handler is None:
            return AgentResult(
                False,
                f"Unsupported action for {self.name}.",
                {
                    "agent": self.name,
                    "supported_actions": sorted(self._handlers()),
                    "manifest": self.manifest.to_dict(),
                },
            )

        product = handler(command)
        return AgentResult(
            True,
            product.summary,
            {
                "agent": self.name,
                "manifest": self.manifest.to_dict(),
                "work_product": product.to_dict(),
            },
        )

    def _handlers(self) -> dict[str, Any]:
        return {"describe_capabilities": self._describe_capabilities}

    def _describe_capabilities(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary=f"{self.name} is ready.",
            artifacts=(
                TaskArtifact(
                    kind="manifest",
                    name=f"{self.name}.manifest",
                    content=str(self.manifest.to_dict()),
                ),
            ),
            next_steps=("Delegate a supported action with an explicit defensive objective.",),
        )


def artifact(kind: str, name: str, lines: tuple[str, ...]) -> TaskArtifact:
    return TaskArtifact(kind=kind, name=name, content="\n".join(lines))


def finding(
    title: str,
    category: str,
    severity: Any,
    location: str | None = None,
    evidence: str | None = None,
    recommendation: str | None = None,
) -> TaskFinding:
    return TaskFinding(
        title=title,
        category=category,
        severity=severity,
        location=location,
        evidence=evidence,
        recommendation=recommendation,
    )
