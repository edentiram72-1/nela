"""Defensive secure code review agent."""

from __future__ import annotations

import re

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class SecureCodeReviewerAgent(SpecialistAgent):
    name = "secure_code_reviewer"
    domain = AgentDomain.SECURITY
    purpose = "Perform defensive SAST-style review and suggest remediation."
    capabilities = ("sast.review", "secure_code.findings", "threat_modeling")

    def _handlers(self):
        return {
            **super()._handlers(),
            "review_code_security": self._review_code_security,
            "threat_model": self._threat_model,
        }

    def _review_code_security(self, command: AgentCommand) -> AgentWorkProduct:
        files = _source_files(command.payload)
        findings: list[TaskFinding] = []
        for path, source in files.items():
            findings.extend(_scan_source(path, source))
        summary = f"Defensive code security review completed for {len(files)} file(s)."
        if not findings:
            summary += " No heuristic findings were detected."
        return AgentWorkProduct(
            summary=summary,
            findings=tuple(findings),
            next_steps=(
                "Confirm findings against real code context.",
                "Patch root causes and add regression tests for each accepted issue.",
            ),
        )

    def _threat_model(self, command: AgentCommand) -> AgentWorkProduct:
        asset = str(command.payload.get("asset", "the changed system"))
        trust_boundaries = tuple(command.payload.get("trust_boundaries", ("user input", "file system", "network/API boundary")))
        findings = tuple(
            TaskFinding(
                title=f"Review trust boundary: {boundary}",
                severity=RiskLevel.MEDIUM,
                category="threat_model",
                location=asset,
                recommendation="Document expected inputs, authentication, authorization, logging, and failure behavior.",
            )
            for boundary in trust_boundaries
        )
        return AgentWorkProduct(
            summary=f"Threat model scaffold prepared for {asset}.",
            findings=findings,
            next_steps=("Convert accepted risks into implementation tasks.",),
        )


def _source_files(payload: dict[str, object]) -> dict[str, str]:
    files = payload.get("files")
    if isinstance(files, dict):
        return {str(path): str(source) for path, source in files.items()}
    return {str(payload.get("path", "inline")): str(payload.get("source", ""))}


def _scan_source(path: str, source: str) -> list[TaskFinding]:
    checks: tuple[tuple[str, str, RiskLevel, str], ...] = (
        (r"\beval\s*\(", "Dynamic eval usage", RiskLevel.HIGH, "Replace eval with a typed parser or explicit dispatch table."),
        (r"\bexec\s*\(", "Dynamic exec usage", RiskLevel.HIGH, "Remove exec or isolate trusted code generation behind review and tests."),
        (r"shell\s*=\s*True", "Shell execution enabled", RiskLevel.HIGH, "Use argument arrays with shell disabled."),
        (r"pickle\.loads?\s*\(", "Unsafe pickle deserialization", RiskLevel.HIGH, "Use a safe serialization format for untrusted data."),
        (r"yaml\.load\s*\((?![^)]*SafeLoader)", "YAML load without SafeLoader", RiskLevel.MEDIUM, "Use yaml.safe_load or SafeLoader."),
        (r"verify\s*=\s*False", "TLS certificate verification disabled", RiskLevel.HIGH, "Keep TLS verification enabled and fix trust roots explicitly."),
        (r"hashlib\.(md5|sha1)\s*\(", "Weak hash algorithm", RiskLevel.MEDIUM, "Use SHA-256 or a password-specific hashing scheme where appropriate."),
        (r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]{8,}", "Possible hardcoded secret", RiskLevel.CRITICAL, "Move secrets to a managed secret store or environment variable."),
    )
    findings: list[TaskFinding] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        for pattern, title, severity, recommendation in checks:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(
                    TaskFinding(
                        title=title,
                        severity=severity,
                        category="sast",
                        location=f"{path}:{line_number}",
                        evidence=line.strip()[:160],
                        recommendation=recommendation,
                    )
                )
    return findings
