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
                "לאמת את הממצאים מול הקוד האמיתי.",
                "לתקן את שורש הבעיה ולהוסיף בדיקת רגרסיה לכל ממצא שאושר.",
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
                recommendation="לתעד קלטים צפויים, אימות, הרשאות, לוגים והתנהגות כשל.",
            )
            for boundary in trust_boundaries
        )
        return AgentWorkProduct(
            summary=f"Threat model scaffold prepared for {asset}.",
            findings=findings,
            next_steps=("להפוך סיכונים שאושרו למשימות יישום קטנות.",),
        )


def _source_files(payload: dict[str, object]) -> dict[str, str]:
    files = payload.get("files")
    if isinstance(files, dict):
        return {str(path): str(source) for path, source in files.items()}
    return {str(payload.get("path", "inline")): str(payload.get("source", ""))}


def _scan_source(path: str, source: str) -> list[TaskFinding]:
    checks: tuple[tuple[str, str, RiskLevel, str], ...] = (
        (r"\beval\s*\(", "Dynamic eval usage", RiskLevel.HIGH, "להחליף eval בפרסר טיפוסי או בטבלת פעולות מפורשת."),
        (r"\bexec\s*\(", "Dynamic exec usage", RiskLevel.HIGH, "להסיר exec או לבודד יצירת קוד מאושרת מאחורי סקירה ובדיקות."),
        (r"shell\s*=\s*True", "Shell execution enabled", RiskLevel.HIGH, "להריץ פקודות כמערך ארגומנטים בלי shell."),
        (r"pickle\.loads?\s*\(", "Unsafe pickle deserialization", RiskLevel.HIGH, "להשתמש בפורמט סריאליזציה בטוח עבור מידע לא מהימן."),
        (r"yaml\.load\s*\((?![^)]*SafeLoader)", "YAML load without SafeLoader", RiskLevel.MEDIUM, "להשתמש ב-yaml.safe_load או SafeLoader."),
        (r"verify\s*=\s*False", "TLS certificate verification disabled", RiskLevel.HIGH, "להשאיר אימות TLS פעיל ולתקן trust roots במפורש."),
        (r"hashlib\.(md5|sha1)\s*\(", "Weak hash algorithm", RiskLevel.MEDIUM, "להשתמש ב-SHA-256 או במנגנון ייעודי לסיסמאות."),
        (r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]{8,}", "Possible hardcoded secret", RiskLevel.CRITICAL, "להעביר סודות למשתני סביבה או למנהל סודות ייעודי."),
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
