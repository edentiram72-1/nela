# Authorized Cyber Lab

The cyber lab is a local control plane for defensive, authorized testing. It
does not perform exploitation, external scanning, credential theft, persistence,
evasion, malware execution, or exfiltration.

## What It Allows

- Register a local or lab target such as `http://localhost:3000`.
- Require an explicit `CyberAuthorization` for active cyber actions.
- Check the action against target allowlists and scope type.
- Record every decision in an audit log.
- Prepare dry-run local scans and deterministic fuzz cases.
- Stop all lab actions with a kill switch.

## What It Blocks

- Public external targets for active lab actions.
- Missing, expired, mismatched, or incomplete authorization.
- Action classes that NELA never performs:
  credential theft, persistence, malware deployment, evasion, exfiltration, and
  external targeting.
- Any request outside the registered target allowlist.

## Minimal Flow

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
        action="run_local_fuzzing",
        payload={
            "target": target,
            "approved": True,
            "dry_run": True,
            "authorization": {
                "owner": "local-owner",
                "scope_type": "local_lab",
                "targets": [target],
                "allowed_actions": ["run_local_fuzzing"],
            },
            "input_types": ["empty", "unicode", "malformed_json"],
        },
    )
)
```

The output is a normalized `work_product` containing the lab decision, audit ID,
deterministic fuzz cases, findings, and next steps.

## Conversation Routing

The Brain can route a small safe set of Hebrew/English security requests to
existing defensive Agents:

- `WorkspaceSecurityScan`: runs a local SAST-style scan over supported source
  and config files in the current workspace through `secure_code_reviewer`.
- `DependencyScan`: parses local dependency manifests through
  `vulnerability_research` and reports version hygiene / supplied advisory
  correlations.
- `SecretsHygieneReview`: reviews supplied text/config for likely exposed
  secrets, tokens, and credential-hygiene issues through `secrets_hygiene`.
- `IdentityAccessReview`: reviews access-control and least-privilege risks
  through `identity_access`.
- `NetworkDefenseReview`: reviews supplied network exposure and TLS posture
  through `network_defense`.
- `SupplyChainReview`: reviews build, release, and supply-chain hygiene through
  `supply_chain_security`.
- `SecurityCapabilitiesQuestion`: explains NELA's defensive cyber boundaries.
- `CyberDefenseSweep`: creates a first defensive posture report through
  `cyber_defense`, including findings, severity, recommendations, and next
  steps.
- `SecurityReview`: delegates passive code/security text review to
  `secure_code_reviewer`.
- `ThreatModel`: delegates threat-model scaffolding to `secure_code_reviewer`.
- `CyberLabStatus`: reads the current authorized lab state through
  `authorized_lab`.
- `CyberLabRegisterTarget`: registers a local/owned lab target through
  `authorized_lab`.
- `LocalFuzzPlan`: prepares a local-only fuzzing plan through
  `anomaly_discovery`.

This does not enable external targeting or active offensive behavior. Active
lab execution remains gated by authorization, target allowlists, scoped
sessions, confirmation, dry-run behavior, audit records, process isolation, and
the kill switch.

Example local route:

```text
User: "תרשמי יעד מעבדה http://localhost:3000"
  -> CyberLabRegisterTarget
  -> authorized_lab.register_lab_target
  -> Permission tier T1

User: "תכיני תוכנית fuzz מקומית לפרסר"
  -> LocalFuzzPlan
  -> anomaly_discovery.create_local_fuzz_plan
  -> Permission tier T0
```

Example defense findings route:

```text
User: "נלה תעשי הגנה"
User: "תעשי בדיקה של אבטחה"
  -> CyberDefenseSweep
  -> cyber_defense.defense_posture_check
  -> Permission tier T0
  -> Hebrew response with findings, severity, recommendation, and next step
```

The first posture check intentionally starts with safe defensive fundamentals:
authorized scope, access control, audit coverage, dependency/config hardening,
and recovery readiness.

Example local code/dependency routes:

```text
User: "נלה תבדקי את הפרויקט לאבטחה"
  -> WorkspaceSecurityScan
  -> secure_code_reviewer.scan_workspace_security
  -> Permission tier T0

User: "תעשי בדיקת תלותים"
  -> DependencyScan
  -> vulnerability_research.scan_workspace_dependencies
  -> Permission tier T0

User: "תעשי בדיקת סודות"
  -> SecretsHygieneReview
  -> secrets_hygiene.review_secrets_hygiene
  -> Permission tier T0

User: "תעשי בדיקת הרשאות"
  -> IdentityAccessReview
  -> identity_access.review_access_controls
  -> Permission tier T0

User: "תעשי בדיקת רשת"
  -> NetworkDefenseReview
  -> network_defense.review_network_exposure
  -> Permission tier T0

User: "תעשי בדיקת שרשרת אספקה"
  -> SupplyChainReview
  -> supply_chain_security.review_supply_chain
  -> Permission tier T0
```

Both routes are local and defensive. They do not contact external targets, do
not exploit vulnerabilities, and redact likely hardcoded secrets from evidence.
