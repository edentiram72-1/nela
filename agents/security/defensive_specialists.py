"""Focused passive cyber-defense specialist agents."""

from __future__ import annotations

import re

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class SecretsHygieneAgent(SpecialistAgent):
    name = "secrets_hygiene"
    domain = AgentDomain.SECURITY
    purpose = "Find likely secret-handling risks in supplied local text or configuration."
    capabilities = ("secrets.review", "secret_rotation.plan", "credential_hygiene")

    def _handlers(self):
        return {**super()._handlers(), "review_secrets_hygiene": self._review_secrets_hygiene}

    def _review_secrets_hygiene(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        findings: list[TaskFinding] = []
        checks = (
            (r"(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[^'\"\s]{8,}", "ייתכן שיש סוד גלוי", RiskLevel.CRITICAL),
            (r"(bearer|basic)\s+[a-z0-9._~+/=-]{12,}", "נראה כמו credential בתוך טקסט", RiskLevel.HIGH),
            (r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----", "מפתח פרטי נמצא בטקסט", RiskLevel.CRITICAL),
            (r"\.env(?:\s|$|/)", "קובץ env דורש בדיקת חשיפה", RiskLevel.MEDIUM),
        )
        for pattern, title, severity in checks:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(
                    TaskFinding(
                        title=title,
                        severity=severity,
                        category="secrets_hygiene",
                        location=str(command.payload.get("target", "conversation")),
                        evidence=_redact(text),
                        recommendation="להוציא סודות מהקוד, לסובב credentials שנחשפו, ולהשתמש במנהל סודות או משתני סביבה מאובטחים.",
                    )
                )
        return AgentWorkProduct(
            summary=f"Secrets hygiene review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            artifacts=(artifact("checklist", "secrets_hygiene", _secrets_checklist()),),
            next_steps=("אם אושר ממצא סוד, לסובב אותו לפני שממשיכים לפתח.",),
        )


class IdentityAccessAgent(SpecialistAgent):
    name = "identity_access"
    domain = AgentDomain.SECURITY
    purpose = "Review access-control and permission posture for least-privilege risks."
    capabilities = ("access.review", "least_privilege", "permission_boundary")

    def _handlers(self):
        return {**super()._handlers(), "review_access_controls": self._review_access_controls}

    def _review_access_controls(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        findings: list[TaskFinding] = []
        checks = (
            (r"\b(admin|owner|root)\b", "הרשאת על דורשת הצדקה", RiskLevel.MEDIUM),
            (r"\b(allow_all|AllowAny|anyone|public-read|public-write)\b", "מדיניות גישה פתוחה מדי", RiskLevel.HIGH),
            (r"\*\s*:\s*\*|\baction\s*:\s*\*", "הרשאה כללית מדי", RiskLevel.HIGH),
            (r"\bskip(_|-)?auth\b|\bauth\s*[:=]\s*false\b", "עקיפת אימות אפשרית", RiskLevel.HIGH),
        )
        for pattern, title, severity in checks:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(
                    TaskFinding(
                        title=title,
                        severity=severity,
                        category="identity_access",
                        location=str(command.payload.get("target", "conversation")),
                        evidence=_redact(text),
                        recommendation="להגדיר בעלים, scope מינימלי, תוקף הרשאה, וביקורת לכל פעולה רגישה.",
                    )
                )
        return AgentWorkProduct(
            summary=f"Identity/access review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            next_steps=("להתחיל מהרשאות רחבות או אימות חסר, כי אלה מעלות סיכון מהר.",),
        )


class NetworkDefenseAgent(SpecialistAgent):
    name = "network_defense"
    domain = AgentDomain.SECURITY
    purpose = "Review supplied network configuration for exposure and transport-security risks."
    capabilities = ("network.exposure.review", "tls.posture", "local_service_hardening")

    def _handlers(self):
        return {**super()._handlers(), "review_network_exposure": self._review_network_exposure}

    def _review_network_exposure(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        findings: list[TaskFinding] = []
        checks = (
            (r"0\.0\.0\.0|::/0|0\.0\.0\.0/0", "חשיפת רשת רחבה", RiskLevel.MEDIUM, "להגביל bind או ingress ל־localhost או לטווח מאושר."),
            (r"\b(http://)[^\s]+", "תקשורת HTTP ללא TLS", RiskLevel.MEDIUM, "להשתמש ב־HTTPS או לתעד חריג מקומי זמני."),
            (r"verify\s*[:=]\s*false|insecure_skip_verify", "אימות TLS כבוי", RiskLevel.HIGH, "להשאיר אימות TLS פעיל ולתקן trust roots במקום לעקוף."),
            (r"\b(22|3389|5432|6379|9200)\b.*\b(public|open|internet)\b", "שירות רגיש נראה חשוף", RiskLevel.HIGH, "לסגור חשיפה ציבורית ולהשתמש ב־VPN, tunnel, או רשת פנימית."),
        )
        for pattern, title, severity, recommendation in checks:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(
                    TaskFinding(
                        title=title,
                        severity=severity,
                        category="network_defense",
                        location=str(command.payload.get("target", "conversation")),
                        evidence=_redact(text),
                        recommendation=recommendation,
                    )
                )
        return AgentWorkProduct(
            summary=f"Network defense review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            next_steps=("לא לבצע סריקה אקטיבית בלי יעד מקומי/מאושר והרשאה מפורשת.",),
        )


class SupplyChainSecurityAgent(SpecialistAgent):
    name = "supply_chain_security"
    domain = AgentDomain.SECURITY
    purpose = "Review dependency, build, and release hygiene for supply-chain risk."
    capabilities = ("supply_chain.review", "build_integrity", "release_hygiene")

    def _handlers(self):
        return {**super()._handlers(), "review_supply_chain": self._review_supply_chain}

    def _review_supply_chain(self, command: AgentCommand) -> AgentWorkProduct:
        text = _text(command)
        findings: list[TaskFinding] = []
        checks = (
            (r":latest\b|\blatest\b", "גרסה לא מקובעת", RiskLevel.MEDIUM, "לקבע גרסאות או digests כדי למנוע שינוי לא צפוי."),
            (r"curl\s+[^|]+?\|\s*(sh|bash)|wget\s+[^|]+?\|\s*(sh|bash)", "הרצת סקריפט מרשת בצינור", RiskLevel.HIGH, "להוריד, לאמת hash/signature, ואז להריץ רק אם המקור מאושר."),
            (r"--no-verify|--ignore-scripts|strict-ssl\s*=\s*false", "עקיפת בדיקות supply-chain", RiskLevel.HIGH, "לא לעקוף אימות או hooks בלי חריג מתועד."),
            (r"(package-lock\.json|poetry\.lock|uv\.lock|pnpm-lock\.yaml|yarn\.lock)", "Lockfile זוהה", RiskLevel.INFO, "לוודא שה־lockfile מחויב ונבדק ב־CI."),
        )
        for pattern, title, severity, recommendation in checks:
            if re.search(pattern, text, flags=re.IGNORECASE):
                findings.append(
                    TaskFinding(
                        title=title,
                        severity=severity,
                        category="supply_chain",
                        location=str(command.payload.get("target", "conversation")),
                        evidence=_redact(text),
                        recommendation=recommendation,
                    )
                )
        return AgentWorkProduct(
            summary=f"Supply-chain review completed with {len(findings)} finding(s).",
            findings=tuple(findings),
            next_steps=("להפריד בין עדכון תלותים, בדיקת advisories, והרצת בדיקות לפני merge.",),
        )


def _text(command: AgentCommand) -> str:
    return str(command.payload.get("text") or command.payload.get("source") or command.payload.get("config") or "")


def _redact(text: str) -> str:
    compact = " ".join(text.split())[:180]
    compact = re.sub(r"(?i)(api[_-]?key|secret|token|password)(\s*[:=]\s*)[^'\"\s]+", r"\1\2[redacted]", compact)
    compact = re.sub(r"(?i)(bearer|basic)\s+[a-z0-9._~+/=-]{8,}", r"\1 [redacted]", compact)
    compact = re.sub(r"-----BEGIN [^-]+PRIVATE KEY-----.*", "-----BEGIN [redacted] PRIVATE KEY-----", compact)
    return compact


def _secrets_checklist() -> tuple[str, ...]:
    return (
        "Search for hardcoded keys, tokens, passwords, and private keys.",
        "Rotate confirmed leaked credentials before merging.",
        "Store runtime secrets outside source control.",
        "Keep evidence redacted in user-facing responses and logs.",
    )
