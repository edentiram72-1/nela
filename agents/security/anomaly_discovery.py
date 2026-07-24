"""Defensive anomaly discovery and local fuzzing-plan agent."""

from __future__ import annotations

from statistics import mean, pstdev

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class AnomalyDiscoveryAgent(SpecialistAgent):
    name = "anomaly_discovery"
    domain = AgentDomain.SECURITY
    purpose = "Find unusual local signals and design safe lab-only fuzzing plans."
    capabilities = ("anomaly.detection", "local.fuzzing.plan", "unknown_unknowns.discovery")

    def _handlers(self):
        return {
            **super()._handlers(),
            "detect_anomalies": self._detect_anomalies,
            "create_local_fuzz_plan": self._create_local_fuzz_plan,
        }

    def _detect_anomalies(self, command: AgentCommand) -> AgentWorkProduct:
        series = tuple(float(value) for value in command.payload.get("series", ()))
        label = str(command.payload.get("label", "metric"))
        if len(series) < 3:
            return AgentWorkProduct(
                summary="Not enough data points for anomaly detection.",
                next_steps=("Provide at least three local observations.",),
            )
        baseline = mean(series)
        deviation = pstdev(series) or 1.0
        findings = []
        for index, value in enumerate(series):
            z_score = abs((value - baseline) / deviation)
            if z_score >= 2.0:
                findings.append(
                    TaskFinding(
                        title=f"Anomalous {label} value",
                        severity=RiskLevel.MEDIUM if z_score < 3.0 else RiskLevel.HIGH,
                        category="anomaly",
                        location=f"{label}[{index}]",
                        evidence=f"value={value}; mean={baseline:.2f}; z={z_score:.2f}",
                        recommendation="Inspect local logs, recent changes, and input shape around this observation.",
                    )
                )
        return AgentWorkProduct(
            summary=f"Anomaly detection completed for {len(series)} local point(s).",
            findings=tuple(findings),
        )

    def _create_local_fuzz_plan(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target", "local parser or function"))
        input_types = tuple(command.payload.get("input_types", ("empty input", "large input", "unicode input", "malformed structure")))
        return AgentWorkProduct(
            summary="Local lab fuzzing plan prepared.",
            artifacts=(
                artifact(
                    "fuzz_plan",
                    "local_fuzz_plan",
                    (
                        f"Target: {target}",
                        "Scope: local/lab execution only, no external targets.",
                        "Harness: call the target through its public function boundary.",
                        "Assertions: no crashes, no hangs, clear validation errors.",
                        "Inputs:",
                        *(f"- {input_type}" for input_type in input_types),
                    ),
                ),
            ),
            next_steps=("Implement the harness in tests before increasing input volume.",),
        )
