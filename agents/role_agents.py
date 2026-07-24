"""Additional first-wave specialist agents for NELA."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding


class QualitySelfEvaluationAgent(SpecialistAgent):
    name = "quality_self_evaluation"
    domain = AgentDomain.QUALITY
    purpose = "Score agent output against requirements, evidence, safety, and test coverage."
    capabilities = ("quality.self_evaluation", "acceptance.gates", "risk.scoring")

    def _handlers(self):
        return {**super()._handlers(), "self_evaluate": self._self_evaluate, "quality_gate": self._quality_gate}

    def _self_evaluate(self, command: AgentCommand) -> AgentWorkProduct:
        criteria = tuple(command.payload.get("criteria", ("requirements met", "tests run", "risks documented")))
        return AgentWorkProduct(
            summary="Self-evaluation checklist prepared.",
            artifacts=(artifact("checklist", "self_evaluation", tuple(f"- {criterion}" for criterion in criteria)),),
            next_steps=("Fail closed if evidence is missing for a required criterion.",),
        )

    def _quality_gate(self, command: AgentCommand) -> AgentWorkProduct:
        missing = tuple(command.payload.get("missing", ()))
        findings = tuple(
            TaskFinding(
                title=f"Missing quality evidence: {item}",
                severity=RiskLevel.MEDIUM,
                category="quality_gate",
                recommendation="Add evidence or mark the task blocked before release.",
            )
            for item in missing
        )
        return AgentWorkProduct(summary=f"Quality gate reviewed {len(missing)} gap(s).", findings=findings)


class TestEngineerAgent(SpecialistAgent):
    name = "test_engineer"
    domain = AgentDomain.QUALITY
    purpose = "Create focused automated test plans and regression suites."
    capabilities = ("test.engineering", "regression.tests", "test.automation")

    def _handlers(self):
        return {**super()._handlers(), "create_test_strategy": self._create_test_strategy}

    def _create_test_strategy(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target", "changed behavior"))
        return AgentWorkProduct(
            summary="Test engineering strategy prepared.",
            artifacts=(
                artifact(
                    "test_strategy",
                    "test_engineering_strategy",
                    (
                        f"Target: {target}",
                        "Unit tests for local behavior.",
                        "Integration tests across agent boundaries.",
                        "Regression tests for security and permission decisions.",
                        "Smoke checks for documented run commands.",
                    ),
                ),
            ),
        )


class MobileEngineerAgent(SpecialistAgent):
    name = "mobile"
    domain = AgentDomain.SOFTWARE
    purpose = "Plan iOS/Android mobile flows, offline state, accessibility, and release constraints."
    capabilities = ("mobile.design", "ios.review", "android.review")

    def _handlers(self):
        return {**super()._handlers(), "plan_mobile_change": self._plan_mobile_change}

    def _plan_mobile_change(self, command: AgentCommand) -> AgentWorkProduct:
        feature = str(command.payload.get("feature", "mobile feature"))
        return AgentWorkProduct(
            summary="Mobile implementation plan prepared.",
            artifacts=(
                artifact(
                    "implementation_plan",
                    "mobile_plan",
                    (
                        f"Feature: {feature}",
                        "Define platform-specific permissions and privacy copy.",
                        "Design offline, background, and interruption states.",
                        "Cover RTL, dynamic text, touch targets, and small screens.",
                        "Add simulator tests for primary flows.",
                    ),
                ),
            ),
        )


class DevOpsEngineerAgent(SpecialistAgent):
    name = "devops"
    domain = AgentDomain.SOFTWARE
    purpose = "Plan deployment, CI/CD, observability, rollback, and runtime hardening."
    capabilities = ("deployment.design", "ci.review", "runtime.operations")

    def _handlers(self):
        return {
            **super()._handlers(),
            "plan_devops_change": self._plan_devops_change,
            "review_deployment_config": self._review_deployment_config,
        }

    def _plan_devops_change(self, command: AgentCommand) -> AgentWorkProduct:
        service = str(command.payload.get("service", "service"))
        return AgentWorkProduct(
            summary="DevOps rollout plan prepared.",
            artifacts=(
                artifact(
                    "rollout_plan",
                    "devops_plan",
                    (
                        f"Service: {service}",
                        "Build reproducible local and CI checks.",
                        "Separate deploy, migrate, and rollback steps.",
                        "Add health checks, logs, metrics, and alert routing.",
                        "Keep secrets outside source and deployment logs.",
                    ),
                ),
            ),
        )

    def _review_deployment_config(self, command: AgentCommand) -> AgentWorkProduct:
        config = str(command.payload.get("config", ""))
        findings = []
        if "latest" in config:
            findings.append(
                TaskFinding(
                    "Floating container tag",
                    RiskLevel.MEDIUM,
                    "deployment",
                    evidence="latest",
                    recommendation="Pin image tags or digests for repeatable deployments.",
                )
            )
        if "privileged: true" in config:
            findings.append(
                TaskFinding(
                    "Privileged container requested",
                    RiskLevel.HIGH,
                    "deployment",
                    evidence="privileged: true",
                    recommendation="Remove privileged mode unless a reviewed exception exists.",
                )
            )
        return AgentWorkProduct(summary="Deployment config review completed.", findings=tuple(findings))


class CodeReviewerAgent(SpecialistAgent):
    name = "code_reviewer"
    domain = AgentDomain.QUALITY
    purpose = "Review code for correctness, maintainability, regressions, and missing tests."
    capabilities = ("code.review", "regression.review", "maintainability.review")

    def _handlers(self):
        return {**super()._handlers(), "review_code_quality": self._review_code_quality}

    def _review_code_quality(self, command: AgentCommand) -> AgentWorkProduct:
        diff = str(command.payload.get("diff", ""))
        findings = []
        if "TODO" in diff or "pass" in diff:
            findings.append(
                TaskFinding(
                    "Incomplete implementation marker",
                    RiskLevel.LOW,
                    "code_review",
                    evidence="TODO/pass",
                    recommendation="Replace placeholders with implementation or track as explicit stub.",
                )
            )
        return AgentWorkProduct(
            summary="Code quality review completed.",
            findings=tuple(findings),
            next_steps=("Prioritize behavioral regressions and missing tests before style feedback.",),
        )


class DocumentationAgent(SpecialistAgent):
    name = "documentation"
    domain = AgentDomain.SOFTWARE
    purpose = "Draft user-facing and developer documentation from implemented behavior."
    capabilities = ("docs.write", "readme.update", "api.documentation")

    def _handlers(self):
        return {**super()._handlers(), "draft_documentation": self._draft_documentation}

    def _draft_documentation(self, command: AgentCommand) -> AgentWorkProduct:
        topic = str(command.payload.get("topic", "feature"))
        return AgentWorkProduct(
            summary="Documentation outline prepared.",
            artifacts=(
                artifact(
                    "documentation",
                    "documentation_outline",
                    (
                        f"# {topic}",
                        "What changed",
                        "How to run it",
                        "Configuration",
                        "Safety and permissions",
                        "Known limits",
                    ),
                ),
            ),
        )


class LLMEngineerAgent(SpecialistAgent):
    name = "llm_engineer"
    domain = AgentDomain.SOFTWARE
    purpose = "Design LLM workflows, prompts, RAG boundaries, evaluation, and tool-use contracts."
    capabilities = ("llm.workflow", "prompt.review", "rag.design")

    def _handlers(self):
        return {**super()._handlers(), "design_llm_workflow": self._design_llm_workflow}

    def _design_llm_workflow(self, command: AgentCommand) -> AgentWorkProduct:
        use_case = str(command.payload.get("use_case", "assistant workflow"))
        return AgentWorkProduct(
            summary="LLM workflow design prepared.",
            artifacts=(
                artifact(
                    "design",
                    "llm_workflow",
                    (
                        f"Use case: {use_case}",
                        "Separate system policy, user intent, retrieved context, and tool results.",
                        "Require grounded citations for external facts.",
                        "Evaluate refusals, hallucination risk, and task completion.",
                    ),
                ),
            ),
        )


class MLEngineerAgent(SpecialistAgent):
    name = "ml_engineer"
    domain = AgentDomain.SOFTWARE
    purpose = "Plan model training, evaluation, feature quality, and drift monitoring."
    capabilities = ("ml.experiment", "model.evaluation", "feature.review")

    def _handlers(self):
        return {**super()._handlers(), "plan_ml_experiment": self._plan_ml_experiment}

    def _plan_ml_experiment(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target", "model"))
        return AgentWorkProduct(
            summary="ML experiment plan prepared.",
            artifacts=(
                artifact(
                    "experiment_plan",
                    "ml_experiment",
                    (
                        f"Target: {target}",
                        "Define baseline, metric, dataset split, and leakage checks.",
                        "Track model card notes and failure modes.",
                        "Add drift and bias review before production use.",
                    ),
                ),
            ),
        )


class DataEngineerAgent(SpecialistAgent):
    name = "data_engineer"
    domain = AgentDomain.SOFTWARE
    purpose = "Design data ingestion, validation, lineage, and quality checks."
    capabilities = ("data.pipeline", "data.quality", "schema.design")

    def _handlers(self):
        return {**super()._handlers(), "plan_data_pipeline": self._plan_data_pipeline}

    def _plan_data_pipeline(self, command: AgentCommand) -> AgentWorkProduct:
        source = str(command.payload.get("source", "data source"))
        return AgentWorkProduct(
            summary="Data pipeline plan prepared.",
            artifacts=(
                artifact(
                    "pipeline_plan",
                    "data_pipeline",
                    (
                        f"Source: {source}",
                        "Validate schema at ingestion.",
                        "Preserve lineage and raw input snapshots.",
                        "Add quality checks for nulls, duplicates, ranges, and freshness.",
                    ),
                ),
            ),
        )


class ResearchAgent(SpecialistAgent):
    name = "research"
    domain = AgentDomain.SOFTWARE
    purpose = "Structure research questions, evidence, assumptions, and decision-ready summaries."
    capabilities = ("research.topic", "evidence.summary", "assumption.tracking")

    def _handlers(self):
        return {**super()._handlers(), "research_topic": self._research_topic}

    def _research_topic(self, command: AgentCommand) -> AgentWorkProduct:
        topic = str(command.payload.get("topic", "topic"))
        return AgentWorkProduct(
            summary="Research brief scaffold prepared.",
            artifacts=(
                artifact(
                    "research_brief",
                    "research_brief",
                    (
                        f"Topic: {topic}",
                        "Known facts",
                        "Open questions",
                        "Primary sources to verify",
                        "Decision implications",
                    ),
                ),
            ),
            next_steps=("Verify drift-prone facts against primary/current sources before use.",),
        )


class DocumentationResearcherAgent(SpecialistAgent):
    name = "documentation_researcher"
    domain = AgentDomain.SOFTWARE
    purpose = "Read official documentation and turn it into implementation guidance."
    capabilities = ("docs.research", "api.guidance", "migration.notes")

    def _handlers(self):
        return {**super()._handlers(), "research_documentation": self._research_documentation}

    def _research_documentation(self, command: AgentCommand) -> AgentWorkProduct:
        library = str(command.payload.get("library", "library"))
        return AgentWorkProduct(
            summary="Documentation research plan prepared.",
            artifacts=(
                artifact(
                    "research_plan",
                    "documentation_research",
                    (
                        f"Library: {library}",
                        "Prefer official docs and changelogs.",
                        "Capture exact version and date.",
                        "Convert examples into local tests before adoption.",
                    ),
                ),
            ),
        )


class TrendMonitorAgent(SpecialistAgent):
    name = "trend_monitor"
    domain = AgentDomain.SOFTWARE
    purpose = "Track technology trends, lifecycle changes, and security-relevant shifts."
    capabilities = ("trend.monitoring", "lifecycle.watch", "risk.trends")

    def _handlers(self):
        return {**super()._handlers(), "summarize_trends": self._summarize_trends}

    def _summarize_trends(self, command: AgentCommand) -> AgentWorkProduct:
        area = str(command.payload.get("area", "technology area"))
        return AgentWorkProduct(
            summary="Trend monitoring brief prepared.",
            artifacts=(
                artifact(
                    "brief",
                    "trend_monitor",
                    (
                        f"Area: {area}",
                        "Track official releases, deprecations, advisories, and ecosystem adoption.",
                        "Flag only changes with a concrete product or security implication.",
                    ),
                ),
            ),
        )


class SecurityResearcherAgent(SpecialistAgent):
    name = "security_researcher"
    domain = AgentDomain.SECURITY
    purpose = "Research vulnerabilities and defensive techniques without weaponization."
    capabilities = ("security.research", "cve.explain", "defensive.education")

    def _handlers(self):
        return {**super()._handlers(), "research_security_topic": self._research_security_topic}

    def _research_security_topic(self, command: AgentCommand) -> AgentWorkProduct:
        topic = str(command.payload.get("topic", "security topic"))
        return AgentWorkProduct(
            summary="Defensive security research brief prepared.",
            artifacts=(
                artifact(
                    "research_brief",
                    "security_research",
                    (
                        f"Topic: {topic}",
                        "Explain impact, affected assets, defensive detections, and remediation.",
                        "Avoid exploit instructions or reusable payloads.",
                        "Verify current CVE/advisory details before release decisions.",
                    ),
                ),
            ),
        )


class InfrastructureSecurityAgent(SpecialistAgent):
    name = "infrastructure_security"
    domain = AgentDomain.SECURITY
    purpose = "Audit infrastructure configuration, identity boundaries, network exposure, and hardening."
    capabilities = ("config.audit", "infrastructure.hardening", "identity.review")

    def _handlers(self):
        return {**super()._handlers(), "audit_infrastructure_config": self._audit_infrastructure_config}

    def _audit_infrastructure_config(self, command: AgentCommand) -> AgentWorkProduct:
        config = str(command.payload.get("config", ""))
        findings = []
        checks = (
            ("0.0.0.0/0", "Broad network exposure", RiskLevel.HIGH, "Restrict ingress to required trusted ranges."),
            ("AllowAny", "Overbroad allow policy", RiskLevel.MEDIUM, "Replace wildcard allow rules with least privilege."),
            ("public-read", "Public object storage", RiskLevel.HIGH, "Disable public access unless explicitly reviewed."),
        )
        for marker, title, severity, recommendation in checks:
            if marker.lower() in config.lower():
                findings.append(TaskFinding(title, severity, "config_audit", evidence=marker, recommendation=recommendation))
        return AgentWorkProduct(summary="Infrastructure security audit completed.", findings=tuple(findings))


class ThreatIntelligenceAgent(SpecialistAgent):
    name = "threat_intelligence"
    domain = AgentDomain.SECURITY
    purpose = "Summarize threat intel defensively and map it to owned assets and controls."
    capabilities = ("threat.intel", "ioc.triage", "defensive.mapping")

    def _handlers(self):
        return {**super()._handlers(), "summarize_threat_intel": self._summarize_threat_intel}

    def _summarize_threat_intel(self, command: AgentCommand) -> AgentWorkProduct:
        indicators = tuple(command.payload.get("indicators", ()))
        lines = tuple(f"Indicator: {indicator} -> verify in owned logs before action." for indicator in indicators)
        return AgentWorkProduct(
            summary=f"Threat intelligence summary prepared for {len(indicators)} indicator(s).",
            artifacts=(artifact("intel_summary", "threat_intel", lines or ("No indicators supplied.",)),),
        )


class SentinelAgent(SpecialistAgent):
    name = "sentinel"
    domain = AgentDomain.SECURITY
    purpose = "Monitor local signals and raise incident candidates for owned systems."
    capabilities = ("monitoring.signal", "alert.triage", "local.telemetry")

    def _handlers(self):
        return {**super()._handlers(), "monitor_signals": self._monitor_signals}

    def _monitor_signals(self, command: AgentCommand) -> AgentWorkProduct:
        signals = command.payload.get("signals", {})
        count = len(signals) if isinstance(signals, dict) else 0
        return AgentWorkProduct(
            summary=f"Sentinel reviewed {count} signal group(s).",
            next_steps=("Escalate only validated local anomalies to incident command.",),
        )


class IncidentCommanderAgent(SpecialistAgent):
    name = "incident_commander"
    domain = AgentDomain.SECURITY
    purpose = "Coordinate incident severity, ownership, containment, evidence, recovery, and lessons learned."
    capabilities = ("incident.triage", "response.coordination", "severity.assignment")

    def _handlers(self):
        return {**super()._handlers(), "triage_incident": self._triage_incident}

    def _triage_incident(self, command: AgentCommand) -> AgentWorkProduct:
        incident = str(command.payload.get("incident", "incident"))
        return AgentWorkProduct(
            summary="Incident command plan prepared.",
            artifacts=(
                artifact(
                    "incident_plan",
                    "incident_response_route",
                    (
                        f"Incident: {incident}",
                        "1. Confirm owned scope and severity.",
                        "2. Preserve evidence before containment when safe.",
                        "3. Contain affected sessions, tokens, hosts, or containers.",
                        "4. Recover from clean state and rotate exposed secrets.",
                        "5. Capture detection and prevention improvements.",
                    ),
                ),
            ),
        )


class ContainmentAgent(SpecialistAgent):
    name = "containment"
    domain = AgentDomain.SECURITY
    purpose = "Prepare and execute approved containment steps inside owned scope."
    capabilities = ("containment.plan", "session.revoke", "host.isolation")

    def _handlers(self):
        return {**super()._handlers(), "contain_incident": self._contain_incident}

    def _contain_incident(self, command: AgentCommand) -> AgentWorkProduct:
        target = str(command.payload.get("target", "owned asset"))
        return AgentWorkProduct(
            summary="Containment action prepared under scoped approval.",
            artifacts=(
                artifact(
                    "containment_plan",
                    "containment_steps",
                    (
                        f"Target: {target}",
                        "Revoke affected sessions or tokens.",
                        "Quarantine affected local host/container.",
                        "Preserve logs before cleanup.",
                    ),
                ),
            ),
        )


class DeceptionAgent(SpecialistAgent):
    name = "deception"
    domain = AgentDomain.SECURITY
    purpose = "Design safe canaries, decoys, and honeypots inside owned environments."
    capabilities = ("deception.plan", "canary.design", "honeypot.local")

    def _handlers(self):
        return {**super()._handlers(), "plan_deception": self._plan_deception}

    def _plan_deception(self, command: AgentCommand) -> AgentWorkProduct:
        asset = str(command.payload.get("asset", "owned environment"))
        return AgentWorkProduct(
            summary="Deception plan prepared.",
            artifacts=(
                artifact(
                    "deception_plan",
                    "deception_controls",
                    (
                        f"Asset: {asset}",
                        "Place canary tokens that never contain real secrets.",
                        "Log touches with correlation IDs.",
                        "Keep decoys inside owned infrastructure only.",
                    ),
                ),
            ),
        )


class ForensicsAgent(SpecialistAgent):
    name = "forensics"
    domain = AgentDomain.SECURITY
    purpose = "Preserve evidence, timeline events, and chain-of-custody notes."
    capabilities = ("forensics.preserve", "timeline.build", "evidence.review")

    def _handlers(self):
        return {**super()._handlers(), "preserve_evidence": self._preserve_evidence}

    def _preserve_evidence(self, command: AgentCommand) -> AgentWorkProduct:
        evidence = tuple(command.payload.get("evidence", ()))
        return AgentWorkProduct(
            summary=f"Forensics preservation checklist prepared for {len(evidence)} item(s).",
            artifacts=(
                artifact(
                    "checklist",
                    "forensics_preservation",
                    (
                        "Hash evidence before analysis.",
                        "Record source, timestamp, collector, and chain-of-custody.",
                        "Analyze copies, not originals.",
                    ),
                ),
            ),
        )


class ThreatHunterAgent(SpecialistAgent):
    name = "threat_hunter"
    domain = AgentDomain.SECURITY
    purpose = "Search owned logs and telemetry for related suspicious patterns."
    capabilities = ("threat.hunting", "log.analysis", "hypothesis.testing")

    def _handlers(self):
        return {**super()._handlers(), "hunt_threats": self._hunt_threats}

    def _hunt_threats(self, command: AgentCommand) -> AgentWorkProduct:
        hypothesis = str(command.payload.get("hypothesis", "suspicious activity"))
        return AgentWorkProduct(
            summary="Threat hunt plan prepared.",
            artifacts=(
                artifact(
                    "hunt_plan",
                    "threat_hunt",
                    (
                        f"Hypothesis: {hypothesis}",
                        "Search only provided or owned logs.",
                        "Preserve raw queries and false positives.",
                        "Escalate matched events to incident command.",
                    ),
                ),
            ),
        )


class RedTeamSimulatorAgent(SpecialistAgent):
    name = "red_team_simulator"
    domain = AgentDomain.SECURITY
    purpose = "Simulate adversary behavior only inside approved local lab or CTF scope."
    capabilities = ("red_team.lab_simulation", "ctf.exercise", "safe.validation")

    def _handlers(self):
        return {**super()._handlers(), "simulate_lab_adversary": self._simulate_lab_adversary}

    def _simulate_lab_adversary(self, command: AgentCommand) -> AgentWorkProduct:
        objective = str(command.payload.get("objective", "exercise control validation"))
        return AgentWorkProduct(
            summary="Lab-only red-team simulation plan prepared.",
            artifacts=(
                artifact(
                    "lab_simulation",
                    "red_team_simulation",
                    (
                        f"Objective: {objective}",
                        "Scope: approved lab/CTF/owned target only.",
                        "Mode: dry-run unless a scoped session explicitly approves execution.",
                        "No persistence, credential theft, malware, evasion, exfiltration, or external targeting.",
                    ),
                ),
            ),
        )


class BlueTeamAgent(SpecialistAgent):
    name = "blue_team"
    domain = AgentDomain.SECURITY
    purpose = "Improve prevention, monitoring, response, and hardening for owned systems."
    capabilities = ("defense.hardening", "monitoring.design", "control.mapping")

    def _handlers(self):
        return {**super()._handlers(), "harden_defenses": self._harden_defenses}

    def _harden_defenses(self, command: AgentCommand) -> AgentWorkProduct:
        asset = str(command.payload.get("asset", "owned asset"))
        return AgentWorkProduct(
            summary="Blue-team hardening plan prepared.",
            artifacts=(
                artifact(
                    "hardening_plan",
                    "blue_team_controls",
                    (
                        f"Asset: {asset}",
                        "Reduce exposed services and permissions.",
                        "Add detection for high-signal events.",
                        "Verify backup, restore, and secret-rotation paths.",
                    ),
                ),
            ),
        )


class PurpleTeamAgent(SpecialistAgent):
    name = "purple_team"
    domain = AgentDomain.SECURITY
    purpose = "Compare simulated adversary actions with defensive detections and close gaps."
    capabilities = ("purple_team.compare", "detection.gap", "control.validation")

    def _handlers(self):
        return {**super()._handlers(), "compare_red_blue": self._compare_red_blue}

    def _compare_red_blue(self, command: AgentCommand) -> AgentWorkProduct:
        red = tuple(command.payload.get("red_actions", ()))
        blue = tuple(command.payload.get("blue_detections", ()))
        gaps = tuple(action for action in red if action not in blue)
        findings = tuple(
            TaskFinding(
                f"Detection gap for {gap}",
                RiskLevel.MEDIUM,
                "purple_team",
                recommendation="Add or tune detection, then rerun the lab simulation.",
            )
            for gap in gaps
        )
        return AgentWorkProduct(summary=f"Purple-team comparison found {len(gaps)} gap(s).", findings=findings)


class ExploitValidationAgent(SpecialistAgent):
    name = "exploit_validation"
    domain = AgentDomain.SECURITY
    purpose = "Validate suspected vulnerabilities only with non-destructive proofs in approved lab scope."
    capabilities = ("exploit.validation.lab", "non_destructive.proof", "finding.validation")

    def _handlers(self):
        return {**super()._handlers(), "validate_exploit_safely": self._validate_exploit_safely}

    def _validate_exploit_safely(self, command: AgentCommand) -> AgentWorkProduct:
        finding_id = str(command.payload.get("finding_id", "finding"))
        return AgentWorkProduct(
            summary="Safe exploit validation plan prepared.",
            artifacts=(
                artifact(
                    "validation_plan",
                    "safe_exploit_validation",
                    (
                        f"Finding: {finding_id}",
                        "Use a non-destructive proof in the approved lab.",
                        "Record expected signal and rollback path.",
                        "Do not produce reusable offensive payloads.",
                    ),
                ),
            ),
        )


class DetectionEngineeringAgent(SpecialistAgent):
    name = "detection_engineering"
    domain = AgentDomain.SECURITY
    purpose = "Generate defensive detection logic such as Sigma and YARA scaffolds."
    capabilities = ("sigma.generate", "yara.generate", "alert.tuning")

    def _handlers(self):
        return {**super()._handlers(), "generate_detection_rules": self._generate_detection_rules}

    def _generate_detection_rules(self, command: AgentCommand) -> AgentWorkProduct:
        name = str(command.payload.get("name", "nela_detection")).replace(" ", "_")
        indicator = str(command.payload.get("indicator", "suspicious_marker"))
        sigma = "\n".join(
            (
                f"title: {name}",
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
        yara = "\n".join(
            (
                f"rule {name}",
                "{",
                "  strings:",
                f"    $marker = \"{indicator}\"",
                "  condition:",
                "    $marker",
                "}",
            )
        )
        return AgentWorkProduct(
            summary="Detection rule scaffolds generated.",
            artifacts=(
                artifact("sigma", f"{name}.sigma.yml", (sigma,)),
                artifact("yara", f"{name}.yar", (yara,)),
            ),
        )


class RecoveryAgent(SpecialistAgent):
    name = "recovery"
    domain = AgentDomain.SECURITY
    purpose = "Plan clean recovery, restoration, secret rotation, and post-incident validation."
    capabilities = ("recovery.plan", "backup.validation", "secret.rotation")

    def _handlers(self):
        return {**super()._handlers(), "plan_recovery": self._plan_recovery}

    def _plan_recovery(self, command: AgentCommand) -> AgentWorkProduct:
        service = str(command.payload.get("service", "service"))
        return AgentWorkProduct(
            summary="Recovery plan prepared.",
            artifacts=(
                artifact(
                    "recovery_plan",
                    "recovery_steps",
                    (
                        f"Service: {service}",
                        "Restore from known-good backup or rebuild from clean image.",
                        "Rotate affected secrets and sessions.",
                        "Run integrity, regression, and detection tests before returning traffic.",
                    ),
                ),
            ),
        )
