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

- `SecurityCapabilitiesQuestion`: explains NELA's defensive cyber boundaries.
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
