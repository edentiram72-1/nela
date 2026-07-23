"""Capability Registry and built-in Agent manifests."""

from __future__ import annotations

from agents.base import BaseAgent
from permissions.models import AgentManifest, Capability, PermissionTier


class CapabilityRegistry:
    """Stores declared Agent manifests and resolves action capabilities."""

    def __init__(self, manifests: tuple[AgentManifest, ...] = ()) -> None:
        self._manifests: dict[str, AgentManifest] = {}
        self._baseline_manifests: dict[str, AgentManifest] = {manifest.agent: manifest for manifest in manifests}
        for manifest in manifests:
            self.register_manifest(manifest)

    def register_manifest(self, manifest: AgentManifest) -> None:
        self._manifests[manifest.agent] = manifest

    def register_agent(self, agent: BaseAgent) -> None:
        manifest = getattr(agent, "permission_manifest", None)
        if manifest is not None:
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

    def manifests(self) -> tuple[AgentManifest, ...]:
        return tuple(self._manifests.values())


def default_capability_registry() -> CapabilityRegistry:
    """Create the default registry for current built-in Agents."""

    return CapabilityRegistry(
        (
            AgentManifest(
                agent="desktop",
                capabilities=(
                    Capability("is_application_running", PermissionTier.T0, "Read local application status."),
                    Capability("detect_application", PermissionTier.T0, "Read local application status."),
                    Capability("status_application", PermissionTier.T0, "Read local application status."),
                    Capability("wait_until_ready", PermissionTier.T0, "Wait for an allowlisted app to become ready."),
                    Capability("launch_application", PermissionTier.T1, "Launch an allowlisted local application."),
                    Capability("ensure_application", PermissionTier.T1, "Launch or focus an allowlisted local application."),
                    Capability("bring_to_front", PermissionTier.T1, "Focus an allowlisted local application."),
                    Capability("switch_application", PermissionTier.T1, "Focus an allowlisted local application."),
                    Capability("focus_application", PermissionTier.T1, "Focus an allowlisted local application."),
                    Capability(
                        "close_application",
                        PermissionTier.T2,
                        "Ask an allowlisted local application to quit.",
                        requires_confirmation=True,
                    ),
                    Capability(
                        "quit_application",
                        PermissionTier.T2,
                        "Ask an allowlisted local application to quit.",
                        requires_confirmation=True,
                    ),
                ),
            ),
            AgentManifest(
                agent="voice",
                capabilities=(
                    Capability("status", PermissionTier.T0, "Read voice status."),
                    Capability("speak", PermissionTier.T1, "Speak local assistant output."),
                    Capability("queue", PermissionTier.T1, "Queue local assistant output."),
                    Capability("queue_speech", PermissionTier.T1, "Queue local assistant output."),
                    Capability("flush_queue", PermissionTier.T1, "Flush queued local speech."),
                    Capability("stop", PermissionTier.T1, "Stop local speech output."),
                    Capability("stop_speaking", PermissionTier.T1, "Stop local speech output."),
                    Capability("interrupt", PermissionTier.T1, "Interrupt local speech output."),
                    Capability("pause", PermissionTier.T1, "Pause local speech output."),
                    Capability("resume", PermissionTier.T1, "Resume local speech output."),
                    Capability("set_enabled", PermissionTier.T1, "Update local voice playback settings."),
                    Capability("configure_profile", PermissionTier.T1, "Update local voice profile settings."),
                ),
            ),
            AgentManifest(
                agent="memory",
                capabilities=(
                    Capability("remember", PermissionTier.T1, "Store user-provided memory."),
                    Capability("retrieve", PermissionTier.T0, "Read stored memory."),
                ),
            ),
            AgentManifest(
                agent="spotify",
                capabilities=(
                    Capability("ensure_application", PermissionTier.T1, "Prepare Spotify placeholder Agent."),
                    Capability("wait_until_ready", PermissionTier.T0, "Wait for Spotify placeholder Agent."),
                    Capability("search_media", PermissionTier.T1, "Search media through placeholder Agent."),
                    Capability("play_media", PermissionTier.T1, "Start media playback through placeholder Agent."),
                ),
            ),
            _placeholder_manifest("terminal"),
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
