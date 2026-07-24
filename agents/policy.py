"""Defensive policy guardrails and sandboxed tool permission profiles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Any


class PolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"


@dataclass(frozen=True)
class PolicyResult:
    decision: PolicyDecision
    reason: str
    matched_terms: tuple[str, ...] = ()

    @property
    def allowed(self) -> bool:
        return self.decision == PolicyDecision.ALLOW


@dataclass(frozen=True)
class ToolPermissionProfile:
    """Sandbox profile for an agent role.

    The first implementation is intentionally declarative. Runtime integrations
    can bind these profiles to real process, file, and network controls later.
    """

    agent: str
    allowed_tools: tuple[str, ...]
    filesystem: str = "workspace_read"
    network: str = "disabled"
    process_execution: str = "disabled"
    may_modify_code: bool = False
    may_contact_external_targets: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "agent": self.agent,
            "allowed_tools": list(self.allowed_tools),
            "filesystem": self.filesystem,
            "network": self.network,
            "process_execution": self.process_execution,
            "may_modify_code": self.may_modify_code,
            "may_contact_external_targets": self.may_contact_external_targets,
        }


DENIED_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bcredential theft\b",
        r"\bsteal(?:ing)?\s+(?:passwords?|credentials?|tokens?)\b",
        r"\bexfiltrat(?:e|ion)\b",
        r"\bpersistence\b",
        r"\bevasion\b",
        r"\bbypass\s+(?:auth|authentication|mfa|edr|av)\b",
        r"\breverse shell\b",
        r"\bweaponiz(?:e|ed|ation)\b",
        r"\bmalware\b",
        r"\bransomware\b",
        r"\bphishing\b",
        r"\bddos\b",
        r"\bexploit\s+(?:kit|payload|chain|against|for)\b",
        r"\battack\s+(?:external|public|third[- ]party|real)\b",
        r"\bscan\s+(?:the\s+)?internet\b",
    )
)


DEFENSIVE_ALLOWED_TERMS: tuple[str, ...] = (
    "sast",
    "dependency scanning",
    "config auditing",
    "local fuzzing",
    "lab fuzzing",
    "anomaly detection",
    "threat modeling",
    "cve correlation",
    "secure code review",
    "defensive",
    "authorized",
)


class DefensivePolicyGuard:
    """Keeps the multi-agent system inside defensive, authorized work."""

    def validate(self, action: str, payload: dict[str, Any] | None = None) -> PolicyResult:
        haystack = _flatten_text({"action": action, "payload": payload or {}})
        matched = tuple(pattern.pattern for pattern in DENIED_PATTERNS if pattern.search(haystack))
        if matched:
            return PolicyResult(
                PolicyDecision.DENY,
                "Request is outside the defensive/authorized scope for NELA security agents.",
                matched,
            )
        if _targets_external_system(action, payload or {}):
            return PolicyResult(
                PolicyDecision.DENY,
                "Security agents are limited to local, lab, or explicitly supplied project artifacts.",
                ("external_target",),
            )
        return PolicyResult(PolicyDecision.ALLOW, "Request is defensive or neutral.")


def default_tool_permissions() -> dict[str, ToolPermissionProfile]:
    """Default sandbox declarations for first-wave specialist agents."""

    read_only = ("read_workspace", "parse_files", "summarize")
    security_read_only = (*read_only, "static_analysis", "dependency_audit", "config_audit")
    return {
        "orchestrator": ToolPermissionProfile("orchestrator", ("delegate", "summarize"), filesystem="none"),
        "planner": ToolPermissionProfile("planner", ("plan", "decompose"), filesystem="none"),
        "memory": ToolPermissionProfile("memory", ("memory_read", "memory_write"), filesystem="workspace_scoped"),
        "learning": ToolPermissionProfile("learning", ("summarize", "recommend_curriculum"), filesystem="workspace_read"),
        "code_architect": ToolPermissionProfile("code_architect", read_only, filesystem="workspace_read"),
        "backend": ToolPermissionProfile("backend", read_only, filesystem="workspace_read", may_modify_code=True),
        "frontend": ToolPermissionProfile("frontend", read_only, filesystem="workspace_read", may_modify_code=True),
        "test_qa": ToolPermissionProfile("test_qa", (*read_only, "run_local_tests"), filesystem="workspace_read", process_execution="local_tests_only"),
        "secure_code_reviewer": ToolPermissionProfile("secure_code_reviewer", security_read_only, filesystem="workspace_read"),
        "vulnerability_research": ToolPermissionProfile("vulnerability_research", (*security_read_only, "cve_correlation"), filesystem="workspace_read"),
        "anomaly_discovery": ToolPermissionProfile("anomaly_discovery", (*security_read_only, "local_fuzz_plan"), filesystem="workspace_read"),
    }


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _targets_external_system(action: str, payload: dict[str, Any]) -> bool:
    if action not in {"create_local_fuzz_plan", "detect_anomalies", "review_code_security", "scan_dependencies", "correlate_cves"}:
        return False
    target = str(payload.get("target", payload.get("url", "")))
    return bool(re.search(r"https?://|ssh://|tcp://", target, flags=re.IGNORECASE))
