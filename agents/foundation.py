"""Base implementation for deterministic specialist agents."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agents.base import AgentCommand, AgentResult, BaseAgent
from agents.policy import DefensivePolicyGuard, ToolPermissionProfile, default_tool_permissions
from agents.task_schema import AgentDomain, AgentWorkProduct, TaskArtifact, TaskFinding
from permissions.models import AgentManifest as PermissionAgentManifest
from permissions.models import Capability, PermissionTier


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
        permissions = default_tool_permissions().get(
            self.name,
            ToolPermissionProfile(self.name, ("summarize",), filesystem="workspace_read"),
        )
        return AgentManifest(
            name=self.name,
            domain=self.domain,
            purpose=self.purpose,
            capabilities=self.capabilities,
            permission_profile=permissions,
        )

    @property
    def permission_manifest(self) -> PermissionAgentManifest:
        capabilities = tuple(
            Capability(
                action=action,
                tier=_permission_tier_for_action(action),
                description=f"{self.name}: {action}",
                requires_confirmation=_permission_tier_for_action(action) in {PermissionTier.T2, PermissionTier.T3},
                scopes=("cyber.authorized_scope",) if _permission_tier_for_action(action) == PermissionTier.T3 else (),
            )
            for action in sorted(self._handlers())
        )
        return PermissionAgentManifest(agent=self.name, capabilities=capabilities)

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


def _permission_tier_for_action(action: str) -> PermissionTier:
    if action in {
        "contain_incident",
        "simulate_lab_adversary",
        "validate_exploit_safely",
        "scan_lab_target",
        "run_local_fuzzing",
    }:
        return PermissionTier.T3
    if action in {"remember", "record_lesson", "teach_response", "register_lab_target"}:
        return PermissionTier.T1
    return PermissionTier.T0
