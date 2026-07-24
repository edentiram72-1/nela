# Multi-Agent Foundation

This document describes the first NELA specialist-agent layer.

## Agents

- `orchestrator`: routes work across specialists and consolidates results.
- `planner`: decomposes goals into small, reviewable tasks.
- `memory`: stores and recalls scoped project lessons.
- `learning`: turns outcomes into reusable learning plans.
- `quality_self_evaluation`: scores output against acceptance and safety gates.
- `code_architect`: designs module boundaries and interface shape.
- `backend`: plans backend contracts and backend review checks.
- `frontend`: plans UI flows, state, accessibility, and review checks.
- `mobile`: plans mobile flows, permissions, and platform constraints.
- `devops`: plans deployment, CI, observability, and rollback.
- `code_reviewer`: reviews correctness, maintainability, and regressions.
- `test_qa`: prepares deterministic local test strategies and quality gates.
- `test_engineer`: creates focused automated test plans.
- `documentation`: drafts user and developer documentation.
- `llm_engineer`: designs LLM workflows, prompts, RAG, and evaluations.
- `ml_engineer`: plans ML experiments and model evaluation.
- `data_engineer`: designs data pipelines and quality checks.
- `research`: structures research briefs and assumptions.
- `documentation_researcher`: turns official docs into implementation guidance.
- `trend_monitor`: monitors ecosystem changes with product impact.
- `security_researcher`: researches vulnerabilities defensively.
- `secure_code_reviewer`: performs defensive SAST-style review.
- `vulnerability_research`: correlates dependencies with supplied advisory/CVE data.
- `infrastructure_security`: audits infrastructure configs and hardening.
- `threat_intelligence`: maps indicators to owned logs and controls.
- `sentinel`: reviews local monitoring signals.
- `incident_commander`: coordinates response lifecycle.
- `containment`: prepares approved containment in owned scope.
- `deception`: designs canaries and honeypots inside owned environments.
- `forensics`: preserves evidence and chain-of-custody.
- `threat_hunter`: hunts owned logs with explicit hypotheses.
- `red_team_simulator`: simulates adversary behavior only in approved lab/CTF scope.
- `blue_team`: designs defensive hardening and monitoring.
- `purple_team`: compares lab simulation actions with defensive coverage.
- `exploit_validation`: validates findings with non-destructive lab proofs only.
- `detection_engineering`: generates Sigma and YARA scaffolds.
- `recovery`: plans clean recovery and secret rotation.
- `anomaly_discovery`: detects local metric anomalies and prepares lab-only fuzzing plans.
- `authorized_lab`: gates local/owned cyber-lab work with target allowlists, authorization, audit logs, dry-run, and kill-switch controls.
- `browser`, `terminal`, `github`, `files`, `automation`: registered tool-facing placeholders.

## Guardrails

Security work is defensive and authorized only. Allowed areas include code
analysis, SAST, dependency scanning, config auditing, local fuzzing plans,
anomaly detection, threat modeling, CVE correlation, and remediation guidance.

The policy guard denies requests for exploitation, persistence, credential
theft, evasion, malware, phishing, DDoS, or attacks against external targets.

Active cyber actions additionally require an authorization object, approved
scope type, target allowlist, scoped session, confirmation, audit record, and
dry-run/kill-switch handling. See `docs/cyber_lab.md`.

## Sandboxed Permissions

Every specialist manifest includes a declarative `permission_profile`:

- `allowed_tools`
- `filesystem`
- `network`
- `process_execution`
- `may_modify_code`
- `may_contact_external_targets`

These profiles are intentionally conservative. The current agents do not call
external services or execute arbitrary commands. Future tool integrations should
enforce these profiles at runtime.

## Usage

```python
from agents import build_default_registry
from agents.base import AgentCommand

registry = build_default_registry()
reviewer = registry.get("secure_code_reviewer")

result = reviewer.execute(
    AgentCommand(
        action="review_code_security",
        payload={"files": {"example.py": "password = 'hardcoded-secret'"}},
    )
)
```

The result contains a normalized `work_product` with findings, artifacts, and
next steps.

## Authorized Lab Example

```python
from agents import build_default_registry
from agents.base import AgentCommand

registry = build_default_registry()
lab = registry.get("authorized_lab")

target = "http://localhost:3000"
lab.execute(
    AgentCommand(
        action="register_lab_target",
        payload={
            "target": target,
            "scope_type": "local_lab",
            "owner": "local-owner",
            "proof": "local development server",
        },
    )
)

result = lab.execute(
    AgentCommand(
        action="scan_lab_target",
        payload={
            "target": target,
            "approved": True,
            "dry_run": True,
            "authorization": {
                "owner": "local-owner",
                "scope_type": "local_lab",
                "targets": [target],
                "allowed_actions": ["scan_lab_target"],
            },
            "files": {"app.py": "subprocess.run(cmd, shell=True)"},
        },
    )
)
```

Public URLs remain blocked for active lab actions. Use source-code review,
configuration review, and dependency review for public owned assets until a
separate non-destructive passive scanner is explicitly implemented.
