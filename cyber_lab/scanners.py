"""Deterministic local-only security analysis helpers."""

from __future__ import annotations

from statistics import mean, pstdev
import re
from typing import Any


def scan_source_text(source: str, path: str = "inline") -> list[dict[str, str]]:
    checks = (
        (r"\beval\s*\(", "high", "Dynamic eval usage", "Replace eval with explicit parsing or dispatch."),
        (r"\bexec\s*\(", "high", "Dynamic exec usage", "Remove exec or confine reviewed trusted code."),
        (r"shell\s*=\s*True", "high", "Shell execution enabled", "Use argv arrays with shell disabled."),
        (r"verify\s*=\s*False", "high", "TLS verification disabled", "Enable TLS verification."),
        (r"pickle\.loads?\s*\(", "high", "Unsafe pickle deserialization", "Use a safe serialization format."),
        (r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]{8,}", "critical", "Possible hardcoded secret", "Move secrets out of code."),
    )
    findings: list[dict[str, str]] = []
    for line_number, line in enumerate(source.splitlines(), start=1):
        for pattern, severity, title, recommendation in checks:
            if re.search(pattern, line, flags=re.IGNORECASE):
                findings.append(
                    {
                        "title": title,
                        "severity": severity,
                        "location": f"{path}:{line_number}",
                        "evidence": line.strip()[:160],
                        "recommendation": recommendation,
                    }
                )
    return findings


def audit_config_text(config: str) -> list[dict[str, str]]:
    checks = (
        ("0.0.0.0/0", "high", "Broad network exposure", "Restrict ingress."),
        ("privileged: true", "high", "Privileged container", "Remove privileged mode."),
        ("public-read", "high", "Public object storage", "Disable public access."),
        ("latest", "medium", "Floating version tag", "Pin versions or digests."),
    )
    lowered = config.lower()
    return [
        {"title": title, "severity": severity, "evidence": marker, "recommendation": recommendation}
        for marker, severity, title, recommendation in checks
        if marker.lower() in lowered
    ]


def build_local_fuzz_cases(input_types: tuple[str, ...] | None = None) -> tuple[str, ...]:
    selected = input_types or ("empty", "large", "unicode", "malformed_json", "boundary_number")
    fixtures = {
        "empty": "",
        "large": "A" * 4096,
        "unicode": "\u05e9\u05dc\u05d5\u05dd \u202e text",
        "malformed_json": "{\"unterminated\": true",
        "boundary_number": str(2**63 - 1),
    }
    return tuple(fixtures.get(item, item) for item in selected)


def detect_numeric_anomalies(series: tuple[float, ...], threshold: float = 2.0) -> list[dict[str, Any]]:
    if len(series) < 3:
        return []
    baseline = mean(series)
    deviation = pstdev(series) or 1.0
    anomalies = []
    for index, value in enumerate(series):
        z_score = abs((value - baseline) / deviation)
        if z_score >= threshold:
            anomalies.append({"index": index, "value": value, "z_score": round(z_score, 3)})
    return anomalies


def correlate_cves(dependencies: dict[str, str], advisory_db: dict[str, list[dict[str, str]]]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for name, version in dependencies.items():
        for advisory in advisory_db.get(name, []):
            findings.append(
                {
                    "dependency": name,
                    "installed": version,
                    "id": advisory.get("id", "unknown"),
                    "severity": advisory.get("severity", "high"),
                    "recommendation": advisory.get("recommendation", "Upgrade to a fixed version."),
                }
            )
    return findings


def generate_sigma_rule(name: str, indicator: str) -> str:
    safe_name = name.replace(" ", "_")
    return "\n".join(
        (
            f"title: {safe_name}",
            "status: experimental",
            "logsource:",
            "  product: application",
            "detection:",
            "  selection:",
            f"    message|contains: '{indicator}'",
            "  condition: selection",
            "level: medium",
        )
    )


def generate_yara_rule(name: str, indicator: str) -> str:
    safe_name = name.replace(" ", "_")
    return "\n".join(
        (
            f"rule {safe_name}",
            "{",
            "  strings:",
            f"    $marker = \"{indicator}\"",
            "  condition:",
            "    $marker",
            "}",
        )
    )
