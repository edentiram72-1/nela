# Multi-Agent Foundation

This document describes the first NELA specialist-agent layer.

## Agents

- `orchestrator`: routes work across specialists and consolidates results.
- `planner`: decomposes goals into small, reviewable tasks.
- `memory`: stores and recalls scoped project lessons.
- `learning`: turns outcomes into reusable learning plans.
- `code_architect`: designs module boundaries and interface shape.
- `backend`: plans backend contracts and backend review checks.
- `frontend`: plans UI flows, state, accessibility, and review checks.
- `test_qa`: prepares deterministic local test strategies and quality gates.
- `secure_code_reviewer`: performs defensive SAST-style review.
- `vulnerability_research`: correlates dependencies with supplied advisory/CVE data.
- `anomaly_discovery`: detects local metric anomalies and prepares lab-only fuzzing plans.

## Guardrails

Security work is defensive and authorized only. Allowed areas include code
analysis, SAST, dependency scanning, config auditing, local fuzzing plans,
anomaly detection, threat modeling, CVE correlation, and remediation guidance.

The policy guard denies requests for exploitation, persistence, credential
theft, evasion, malware, phishing, DDoS, or attacks against external targets.

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
