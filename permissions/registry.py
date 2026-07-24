"""Capability Registry and built-in Agent manifests."""

from __future__ import annotations

from agents.base import BaseAgent
from permissions.models import AgentManifest, Capability, PermissionTier, manifest_fingerprint


class ManifestRegistrationError(ValueError):
    """Raised when a manifest cannot be registered safely."""


TIER_ORDER = {
    PermissionTier.T0: 0,
    PermissionTier.T1: 1,
    PermissionTier.T2: 2,
    PermissionTier.T3: 3,
    PermissionTier.T4: 4,
}

MINIMUM_CAPABILITY_TIERS = {
    "desktop.application.status": PermissionTier.T0,
    "desktop.application.launch": PermissionTier.T1,
    "desktop.application.focus": PermissionTier.T1,
    "desktop.application.close": PermissionTier.T2,
    "terminal.command.preview": PermissionTier.T0,
    "terminal.working_directory.get": PermissionTier.T0,
    "terminal.command.execute_allowlisted": PermissionTier.T2,
    "coding.repository.inspect": PermissionTier.T0,
    "coding.tests.run": PermissionTier.T1,
    "coding.diff.review": PermissionTier.T0,
    "coding.task.plan": PermissionTier.T0,
    "coding.files.write": PermissionTier.T2,
    "coding.git.commit": PermissionTier.T2,
    "cyber.passive.analysis": PermissionTier.T0,
}


class CapabilityRegistry:
    """Stores declared Agent manifests and resolves action capabilities."""

    def __init__(self, manifests: tuple[AgentManifest, ...] = ()) -> None:
        self._manifests: dict[str, AgentManifest] = {}
        self._baseline_manifests: dict[str, AgentManifest] = {manifest.agent: manifest for manifest in manifests}
        self.registration_audit: list[dict[str, object]] = []
        for manifest in manifests:
            self.register_manifest(manifest)

    def register_manifest(self, manifest: AgentManifest) -> None:
        self.validate_manifest(manifest)
        if manifest.agent in self._manifests:
            self.registration_audit.append({"agent": manifest.agent, "version": manifest.version, "result": "rejected_duplicate"})
            raise ManifestRegistrationError(f"Manifest for Agent '{manifest.agent}' already exists.")
        self._store_manifest(manifest, result="registered")

    def replace_manifest(self, manifest: AgentManifest, expected_fingerprint: str) -> None:
        self.validate_manifest(manifest)
        if manifest.agent not in self._manifests:
            self.registration_audit.append({"agent": manifest.agent, "version": manifest.version, "result": "rejected_missing_replacement"})
            raise ManifestRegistrationError(f"Manifest for Agent '{manifest.agent}' cannot be replaced because it is not registered.")
        if manifest_fingerprint(manifest) != expected_fingerprint:
            self.registration_audit.append({"agent": manifest.agent, "version": manifest.version, "result": "rejected_manifest_fingerprint"})
            raise ManifestRegistrationError("Replacement manifest fingerprint does not match authorization.")
        self._store_manifest(manifest, result="replaced")

    def _store_manifest(self, manifest: AgentManifest, result: str) -> None:
        self._manifests.update({manifest.agent: manifest})
        self.registration_audit.append({"agent": manifest.agent, "version": manifest.version, "result": result})

    def register_agent(self, agent: BaseAgent) -> None:
        manifest = getattr(agent, "permission_manifest", None)
        if manifest is not None:
            if manifest.agent != agent.name:
                self.registration_audit.append({"agent": agent.name, "version": getattr(manifest, "version", None), "result": "rejected_identity"})
                raise ManifestRegistrationError("Manifest agent identity must match the registered Agent.")
            self.register_manifest(manifest)
            return
        if agent.name not in self._manifests:
            self.register_manifest(AgentManifest(agent=agent.name))

    def unregister_agent(self, agent_name: str) -> None:
        baseline = self._baseline_manifests.get(agent_name)
        if baseline is not None:
            self._manifests[agent_name] = baseline
            return
        self._manifests.pop(agent_name, None)

    def manifest_for(self, agent_name: str) -> AgentManifest | None:
        return self._manifests.get(agent_name)

    def capability_for(self, agent_name: str, action: str) -> Capability | None:
        manifest = self.manifest_for(agent_name)
        return manifest.capability_for(action) if manifest else None

    def find_agents_for_capability(self, capability_id: str, platform: str | None = None) -> tuple[str, ...]:
        agents: list[str] = []
        for manifest in self._manifests.values():
            capability = manifest.capability_for(capability_id)
            if capability is None:
                continue
            if platform and capability.platforms and platform not in capability.platforms:
                continue
            agents.append(manifest.agent)
        return tuple(sorted(agents))

    def list_capabilities(self) -> tuple[str, ...]:
        capabilities = {
            capability.action
            for manifest in self._manifests.values()
            for capability in manifest.capabilities
        }
        return tuple(sorted(capabilities))

    def validate_manifest(self, manifest: AgentManifest) -> None:
        if not manifest.agent or not manifest.agent.strip():
            raise ManifestRegistrationError("Manifest must include an Agent ID.")
        if not manifest.version or not manifest.version.strip():
            raise ManifestRegistrationError("Manifest must include a version.")
        seen: set[str] = set()
        for capability in manifest.capabilities:
            if not capability.action:
                raise ManifestRegistrationError("Capability ID is required.")
            if capability.action in seen:
                raise ManifestRegistrationError(f"Duplicate capability '{capability.action}' in manifest.")
            minimum_tier = MINIMUM_CAPABILITY_TIERS.get(capability.action)
            if minimum_tier is not None and TIER_ORDER[capability.tier] < TIER_ORDER[minimum_tier]:
                raise ManifestRegistrationError(
                    f"Capability '{capability.action}' cannot claim lower than {minimum_tier.value}."
                )
            seen.add(capability.action)

    def manifests(self) -> tuple[AgentManifest, ...]:
        return tuple(self._manifests.values())


def default_capability_registry() -> CapabilityRegistry:
    """Create the default registry for current built-in Agents."""

    return CapabilityRegistry(
        (
            AgentManifest(
                agent="desktop",
                capabilities=(
                    Capability("desktop.application.status", PermissionTier.T0, "Read local application status.", actions=("is_application_running", "detect_application", "status_application", "wait_until_ready"), platforms=("macos",)),
                    Capability("desktop.application.launch", PermissionTier.T1, "Launch an allowlisted local application.", actions=("launch_application", "ensure_application"), platforms=("macos",)),
                    Capability("desktop.application.focus", PermissionTier.T1, "Focus an allowlisted local application.", actions=("bring_to_front", "switch_application", "focus_application"), platforms=("macos",)),
                    Capability(
                        "desktop.application.close",
                        PermissionTier.T2,
                        "Ask an allowlisted local application to quit.",
                        actions=("close_application", "quit_application"),
                        platforms=("macos",),
                        requires_confirmation=True,
                    ),
                ),
            ),
            AgentManifest(
                agent="voice",
                capabilities=(
                    Capability("voice.status", PermissionTier.T0, "Read voice status.", actions=("status",)),
                    Capability("voice.speak", PermissionTier.T1, "Speak local assistant output.", actions=("speak", "queue", "queue_speech", "flush_queue", "stop", "stop_speaking", "interrupt", "pause", "resume", "set_enabled", "configure_profile")),
                ),
            ),
            AgentManifest(
                agent="memory",
                capabilities=(
                    Capability("memory.write", PermissionTier.T1, "Store user-provided memory.", actions=("remember",)),
                    Capability("memory.read", PermissionTier.T0, "Read stored memory.", actions=("retrieve",)),
                ),
            ),
            AgentManifest(
                agent="spotify",
                capabilities=(
                    Capability("media.application.prepare", PermissionTier.T1, "Prepare Spotify placeholder Agent.", actions=("ensure_application",)),
                    Capability("media.application.status", PermissionTier.T0, "Wait for Spotify placeholder Agent.", actions=("wait_until_ready",)),
                    Capability("media.search", PermissionTier.T1, "Search media through placeholder Agent.", actions=("search_media",)),
                    Capability("media.play", PermissionTier.T1, "Start media playback through placeholder Agent.", actions=("play_media",)),
                ),
            ),
            AgentManifest(
                agent="terminal",
                capabilities=(
                    Capability("terminal.command.preview", PermissionTier.T0, "Preview an allowlisted terminal command.", actions=("preview",)),
                    Capability("terminal.working_directory.get", PermissionTier.T0, "Read terminal working directory.", actions=("get_working_directory",)),
                    Capability(
                        "terminal.command.execute_allowlisted",
                        PermissionTier.T2,
                        "Disabled foundation for future allowlisted command execution.",
                        actions=("execute_allowlisted",),
                        requires_confirmation=True,
                        enabled=False,
                    ),
                ),
            ),
            AgentManifest(
                agent="coding",
                capabilities=(
                    Capability("coding.repository.inspect", PermissionTier.T0, "Inspect repository metadata."),
                    Capability("coding.tests.run", PermissionTier.T1, "Run tests in an allowlisted repository."),
                    Capability("coding.diff.review", PermissionTier.T0, "Review diffs without modifying files."),
                    Capability("coding.task.plan", PermissionTier.T0, "Plan coding work without side effects."),
                    Capability("coding.files.write", PermissionTier.T2, "Disabled foundation for future file writes.", requires_confirmation=True, enabled=False),
                    Capability("coding.git.commit", PermissionTier.T2, "Disabled foundation for future commits.", requires_confirmation=True, enabled=False),
                ),
            ),
            _placeholder_manifest("browser"),
            _placeholder_manifest("files"),
            _placeholder_manifest("calendar"),
            _placeholder_manifest("gmail"),
            _placeholder_manifest("github"),
            _placeholder_manifest("codex"),
            _placeholder_manifest("automation"),
            _placeholder_manifest("vision"),
            _placeholder_manifest("claude"),
        )
    )


def _placeholder_manifest(agent: str) -> AgentManifest:
    return AgentManifest(
        agent=agent,
        capabilities=(
            Capability("status", PermissionTier.T0, "Read placeholder Agent status."),
            Capability("health_check", PermissionTier.T0, "Read placeholder Agent health."),
        ),
    )
