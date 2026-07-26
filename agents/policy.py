"""Defensive policy guardrails and sandboxed tool permission profiles."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import ipaddress
import re
import socket
from typing import Any
from urllib.parse import urlparse


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

CYBER_ACTIONS_REQUIRING_AUTHORIZATION: frozenset[str] = frozenset(
    {
        "contain_incident",
        "scan_lab_target",
        "simulate_lab_adversary",
        "validate_exploit_safely",
        "run_local_fuzzing",
    }
)

AUTHORIZED_SCOPE_TYPES: frozenset[str] = frozenset({"local_lab", "ctf", "owned_asset", "workspace_artifact"})

FORBIDDEN_CYBER_ACTIONS: frozenset[str] = frozenset(
    {
        "external_targeting",
        "persistence",
        "credential_theft",
        "malware_deployment",
        "evasion",
        "exfiltration",
    }
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
        payload = payload or {}
        haystack = _flatten_text({"action": action, "payload": _payload_for_text_policy(payload)})
        matched = tuple(pattern.pattern for pattern in DENIED_PATTERNS if pattern.search(haystack))
        if matched:
            return PolicyResult(
                PolicyDecision.DENY,
                "Request is outside the defensive/authorized scope for NELA security agents.",
                matched,
            )
        if _targets_external_system(action, payload):
            return PolicyResult(
                PolicyDecision.DENY,
                "Security agents are limited to local, lab, or explicitly supplied project artifacts.",
                ("external_target",),
            )
        if action in CYBER_ACTIONS_REQUIRING_AUTHORIZATION:
            auth_result = _validate_authorization(action, payload)
            if auth_result is not None:
                return auth_result
        return PolicyResult(PolicyDecision.ALLOW, "Request is defensive or neutral.")


def default_tool_permissions() -> dict[str, ToolPermissionProfile]:
    """Default sandbox declarations for first-wave specialist agents."""

    read_only = ("read_workspace", "parse_files", "summarize")
    security_read_only = (*read_only, "static_analysis", "dependency_audit", "config_audit")
    permissions = {
        "orchestrator": ToolPermissionProfile("orchestrator", ("delegate", "summarize"), filesystem="none"),
        "planner": ToolPermissionProfile("planner", ("plan", "decompose"), filesystem="none"),
        "memory": ToolPermissionProfile("memory", ("memory_read", "memory_write"), filesystem="workspace_scoped"),
        "learning": ToolPermissionProfile("learning", ("summarize", "recommend_curriculum", "language_learning"), filesystem="workspace_scoped"),
        "quality_self_evaluation": ToolPermissionProfile("quality_self_evaluation", read_only, filesystem="workspace_read"),
        "code_architect": ToolPermissionProfile("code_architect", read_only, filesystem="workspace_read"),
        "backend": ToolPermissionProfile("backend", read_only, filesystem="workspace_read", may_modify_code=True),
        "frontend": ToolPermissionProfile("frontend", read_only, filesystem="workspace_read", may_modify_code=True),
        "mobile": ToolPermissionProfile("mobile", read_only, filesystem="workspace_read", may_modify_code=True),
        "devops": ToolPermissionProfile("devops", (*read_only, "config_audit"), filesystem="workspace_read", process_execution="disabled"),
        "code_reviewer": ToolPermissionProfile("code_reviewer", read_only, filesystem="workspace_read"),
        "test_qa": ToolPermissionProfile("test_qa", (*read_only, "run_local_tests"), filesystem="workspace_read", process_execution="local_tests_only"),
        "test_engineer": ToolPermissionProfile("test_engineer", (*read_only, "run_local_tests"), filesystem="workspace_read", process_execution="local_tests_only"),
        "documentation": ToolPermissionProfile("documentation", (*read_only, "draft_docs"), filesystem="workspace_read", may_modify_code=True),
        "llm_engineer": ToolPermissionProfile("llm_engineer", read_only, filesystem="workspace_read"),
        "ml_engineer": ToolPermissionProfile("ml_engineer", read_only, filesystem="workspace_read"),
        "data_engineer": ToolPermissionProfile("data_engineer", read_only, filesystem="workspace_read"),
        "research": ToolPermissionProfile("research", ("summarize", "parse_files"), filesystem="workspace_read", network="approved_sources_only"),
        "documentation_researcher": ToolPermissionProfile("documentation_researcher", ("summarize", "parse_files"), filesystem="workspace_read", network="approved_sources_only"),
        "trend_monitor": ToolPermissionProfile("trend_monitor", ("summarize",), filesystem="none", network="approved_sources_only"),
        "security_researcher": ToolPermissionProfile("security_researcher", (*security_read_only, "threat_model"), filesystem="workspace_read"),
        "secrets_hygiene": ToolPermissionProfile("secrets_hygiene", (*security_read_only, "secret_redaction"), filesystem="workspace_read"),
        "identity_access": ToolPermissionProfile("identity_access", (*security_read_only, "least_privilege"), filesystem="workspace_read"),
        "network_defense": ToolPermissionProfile("network_defense", (*security_read_only, "network_exposure_review"), filesystem="workspace_read", network="disabled"),
        "supply_chain_security": ToolPermissionProfile("supply_chain_security", (*security_read_only, "build_integrity"), filesystem="workspace_read", network="disabled"),
        "secure_code_reviewer": ToolPermissionProfile("secure_code_reviewer", security_read_only, filesystem="workspace_read"),
        "vulnerability_research": ToolPermissionProfile("vulnerability_research", (*security_read_only, "cve_correlation"), filesystem="workspace_read"),
        "authorized_lab": ToolPermissionProfile(
            "authorized_lab",
            (*security_read_only, "authorized_lab", "local_fuzz_plan", "dry_run"),
            filesystem="lab_only",
            network="lab_only",
            process_execution="approved_lab_only",
        ),
        "infrastructure_security": ToolPermissionProfile("infrastructure_security", (*security_read_only, "config_audit"), filesystem="workspace_read"),
        "threat_intelligence": ToolPermissionProfile("threat_intelligence", (*read_only, "ioc_triage"), filesystem="workspace_read", network="approved_sources_only"),
        "sentinel": ToolPermissionProfile("sentinel", (*read_only, "local_telemetry"), filesystem="workspace_read"),
        "incident_commander": ToolPermissionProfile("incident_commander", ("delegate", "summarize", "audit_read"), filesystem="workspace_read"),
        "containment": ToolPermissionProfile("containment", ("session_revoke", "isolate_container", "preserve_logs"), filesystem="workspace_scoped", process_execution="approved_lab_only"),
        "deception": ToolPermissionProfile("deception", (*read_only, "canary_design"), filesystem="workspace_read"),
        "forensics": ToolPermissionProfile("forensics", (*read_only, "hash_evidence"), filesystem="workspace_read"),
        "threat_hunter": ToolPermissionProfile("threat_hunter", (*read_only, "log_query"), filesystem="workspace_read"),
        "red_team_simulator": ToolPermissionProfile("red_team_simulator", ("lab_simulation", "dry_run"), filesystem="lab_only", network="lab_only", process_execution="approved_lab_only"),
        "blue_team": ToolPermissionProfile("blue_team", (*security_read_only, "hardening"), filesystem="workspace_read"),
        "purple_team": ToolPermissionProfile("purple_team", (*security_read_only, "gap_analysis"), filesystem="workspace_read"),
        "exploit_validation": ToolPermissionProfile("exploit_validation", ("non_destructive_validation", "dry_run"), filesystem="lab_only", network="lab_only", process_execution="approved_lab_only"),
        "detection_engineering": ToolPermissionProfile("detection_engineering", (*read_only, "sigma_generate", "yara_generate"), filesystem="workspace_read"),
        "recovery": ToolPermissionProfile("recovery", (*read_only, "recovery_plan"), filesystem="workspace_read"),
        "anomaly_discovery": ToolPermissionProfile("anomaly_discovery", (*security_read_only, "local_fuzz_plan"), filesystem="workspace_read"),
    }
    for name in ("browser", "terminal", "github", "files", "automation"):
        permissions[name] = ToolPermissionProfile(name, ("status", "health_check"), filesystem="workspace_read")
    return permissions


def _flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten_text(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple, set)):
        return " ".join(_flatten_text(item) for item in value)
    return str(value)


def _payload_for_text_policy(payload: dict[str, Any]) -> dict[str, Any]:
    sanitized = dict(payload)
    authorization = sanitized.get("authorization")
    if isinstance(authorization, dict):
        sanitized["authorization"] = {
            key: value
            for key, value in authorization.items()
            if key != "forbidden_actions"
        }
    return sanitized


def _targets_external_system(action: str, payload: dict[str, Any]) -> bool:
    if action not in {
        "create_local_fuzz_plan",
        "detect_anomalies",
        "review_code_security",
        "scan_dependencies",
        "correlate_cves",
        "register_lab_target",
        "evaluate_lab_action",
        "contain_incident",
        "simulate_lab_adversary",
        "validate_exploit_safely",
        "scan_lab_target",
        "run_local_fuzzing",
    }:
        return False
    target = str(payload.get("target", payload.get("url", "")))
    return _looks_external_target(target)


def _validate_authorization(action: str, payload: dict[str, Any]) -> PolicyResult | None:
    authorization = payload.get("authorization")
    if not isinstance(authorization, dict):
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber actions require an explicit authorization object.",
            ("missing_authorization",),
        )
    scope_type = str(authorization.get("scope_type", ""))
    if scope_type not in AUTHORIZED_SCOPE_TYPES:
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber actions are limited to local lab, CTF, owned asset, or workspace artifact scope.",
            ("invalid_scope_type",),
        )
    forbidden = set(str(item) for item in authorization.get("forbidden_actions", ()))
    allowed_actions = set(str(item) for item in authorization.get("allowed_actions", ()))
    if action in FORBIDDEN_CYBER_ACTIONS or action in forbidden:
        return PolicyResult(
            PolicyDecision.DENY,
            "Authorization includes actions that NELA never performs.",
            (action,),
        )
    if allowed_actions & FORBIDDEN_CYBER_ACTIONS:
        return PolicyResult(
            PolicyDecision.DENY,
            "Authorization cannot approve forbidden cyber action classes.",
            tuple(sorted(allowed_actions & FORBIDDEN_CYBER_ACTIONS)),
        )
    if action not in allowed_actions:
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber action is not listed in the approved authorization scope.",
            ("action_not_allowed",),
        )
    target = str(payload.get("target", ""))
    targets = set(str(item) for item in authorization.get("targets", ()))
    if target and targets and target not in targets:
        return PolicyResult(
            PolicyDecision.DENY,
            "Cyber target is outside the approved allowlist.",
            ("target_not_allowed",),
        )
    return None


def _looks_external_target(target: str) -> bool:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "ssh", "tcp"}:
        host = parsed.hostname
        if host is None:
            return True
        return not _is_local_or_private_host(host)
    try:
        address = ipaddress.ip_address(target)
    except ValueError:
        return False
    return not (address.is_loopback or address.is_private)


def _is_local_or_private_host(host: str) -> bool:
    normalized = host.lower().strip("[]")
    if normalized in {"localhost", "127.0.0.1", "::1"} or normalized.endswith(".local"):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        try:
            address = ipaddress.ip_address(socket.gethostbyname(normalized))
        except OSError:
            return False
    return address.is_loopback or address.is_private
