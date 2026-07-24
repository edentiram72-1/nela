"""Agent registry for discovery and delegation."""

from __future__ import annotations

from dataclasses import dataclass

from agents.base import BaseAgent
from permissions.models import AgentManifest, manifest_fingerprint


class DuplicateAgentError(ValueError):
    """Raised when an Agent ID is already registered."""


class AgentReplacementError(ValueError):
    """Raised when an Agent replacement is not explicitly authorized."""


@dataclass(frozen=True)
class ReplacementAuthorization:
    """Administrative proof for one exact Agent replacement."""

    agent: str
    version: str
    manifest_fingerprint: str
    approved_by: str


def authorize_replacement(agent: BaseAgent, approved_by: str) -> ReplacementAuthorization:
    """Create explicit replacement authorization for the exact Agent manifest."""

    manifest = _required_manifest(agent)
    return ReplacementAuthorization(
        agent=agent.name,
        version=manifest.version,
        manifest_fingerprint=manifest_fingerprint(manifest),
        approved_by=approved_by,
    )


class AgentRegistry:
    """Stores available agents by name."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self.registration_audit: list[dict[str, str]] = []

    def register(self, agent: BaseAgent) -> None:
        if agent.name in self._agents:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_duplicate"})
            raise DuplicateAgentError(f"Agent '{agent.name}' is already registered.")
        self._store(agent, result="registered")

    def replace(self, agent: BaseAgent, authorization: ReplacementAuthorization | None = None) -> None:
        if agent.name not in self._agents:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_missing_replacement"})
            raise AgentReplacementError(f"Agent '{agent.name}' cannot be replaced because it is not registered.")
        if self._agents[agent.name] is agent:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_self_replacement"})
            raise AgentReplacementError("Agents cannot replace themselves.")
        self._validate_replacement(agent, authorization)
        self._store(agent, result="replaced", replace_existing=True)

    def _store(self, agent: BaseAgent, result: str, replace_existing: bool = False) -> None:
        if agent.name in self._agents and not replace_existing:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_duplicate"})
            raise DuplicateAgentError(f"Agent '{agent.name}' is already registered.")
        if agent.name not in self._agents and replace_existing:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_missing_replacement"})
            raise AgentReplacementError(f"Agent '{agent.name}' cannot be replaced because it is not registered.")
        self._agents.update({agent.name: agent})
        self.registration_audit.append({"agent": agent.name, "result": result})

    def _validate_replacement(
        self,
        agent: BaseAgent,
        authorization: ReplacementAuthorization | None,
    ) -> None:
        if authorization is None:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_missing_authorization"})
            raise AgentReplacementError("Agent replacement requires explicit authorization.")
        manifest = _required_manifest(agent)
        if manifest.agent != agent.name:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_manifest_identity"})
            raise AgentReplacementError("Replacement manifest identity must match the Agent ID.")
        fingerprint = manifest_fingerprint(manifest)
        if authorization.agent != agent.name or authorization.version != manifest.version:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_authorization_identity"})
            raise AgentReplacementError("Replacement authorization does not match the Agent ID and version.")
        if authorization.manifest_fingerprint != fingerprint:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_manifest_fingerprint"})
            raise AgentReplacementError("Replacement manifest fingerprint does not match authorization.")
        if authorization.approved_by == agent.name:
            self.registration_audit.append({"agent": agent.name, "result": "rejected_self_approved"})
            raise AgentReplacementError("Agents cannot approve their own replacement.")

    def unregister(self, name: str) -> bool:
        return self._agents.pop(name, None) is not None

    def get(self, name: str) -> BaseAgent | None:
        return self._agents.get(name)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._agents))

    def health_check(self) -> dict[str, object]:
        return {name: agent.health_check() for name, agent in self._agents.items()}


def _required_manifest(agent: BaseAgent) -> AgentManifest:
    manifest = getattr(agent, "permission_manifest", None)
    if not isinstance(manifest, AgentManifest):
        raise AgentReplacementError("Agent replacement requires a valid AgentManifest.")
    return manifest
