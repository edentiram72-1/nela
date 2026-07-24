# Claude Sprint 2 Review Bundle

Branch: `feature/NELA-safety-spine-routing`

Implementation commit verified before PR preparation: `8a86b1f`

Base branch: `develop`

Repository: `https://github.com/edentiram72-1/nela`

Compare URL:

```text
https://github.com/edentiram72-1/nela/compare/develop...feature/NELA-safety-spine-routing?expand=1
```

## Review Request

Please review Sprint 2 as a safety and architecture review. Do not assume any
merge approval. Focus on the ship-blocking findings:

- A1: WebView bridge authentication.
- K1: Kill switch process isolation.
- P1: TOCTOU protection.
- P2: Confirmation binding.
- R1: Agent registry overwrite.
- L1: Tamper-evident audit log.
- T1: Authorization before final routing.
- T2: Prompt injection into routing.

## Architecture Summary

Sprint 2 creates the first Safety Spine for NELA OS. The Brain remains
agent-neutral and does not perform external actions. It produces structured
intents and semantic tasks. The Dispatcher resolves candidate Agents through
the Capability Registry, asks the Permission Engine to authorize candidates, and
executes only after authorization succeeds.

Required flow:

```text
Intent
-> candidate capability set
-> policy eligibility
-> authorized candidate set
-> Agent selection
-> final scope validation
-> execution
```

## Files Changed

```text
agents/process_isolation.py
agents/registry.py
brain/applications.py
brain/conversation.py
brain/decision.py
brain/dispatcher.py
brain/intent_router.py
brain/planner.py
core/events.py
docs/agent_registry.md
docs/ai_handoff.md
docs/ai_inbox.md
docs/ai_system_roadmap.md
docs/audit_and_recovery.md
docs/capability_routing.md
docs/coding_agent_spec.md
docs/cyber_agent_spec.md
docs/decisions.md
docs/multi_agent_orchestration.md
docs/nela_runtime_architecture.md
docs/permission_engine.md
docs/permission_model.md
docs/process_isolation.md
docs/safety_spine_verification_criteria.md
docs/secure_ui_bridge.md
docs/sprint2_claude_findings_status.md
permissions/__init__.py
permissions/audit.py
permissions/confirmation.py
permissions/engine.py
permissions/models.py
permissions/registry.py
permissions/scope.py
tests/test_audit_log.py
tests/test_conversation_confirmations.py
tests/test_dispatcher.py
tests/test_events.py
tests/test_intent_recognition.py
tests/test_permission_engine.py
tests/test_planner.py
tests/test_process_isolation.py
tests/test_secure_bridge.py
ui/events.py
ui/secure_bridge.py
```

## Security-Sensitive Files

- `permissions/engine.py`: central authorization gateway.
- `permissions/models.py`: permission tiers, requests, decisions, manifests.
- `permissions/registry.py`: capability registry and manifest validation.
- `permissions/confirmation.py`: exact action tuple confirmation hash.
- `permissions/scope.py`: filesystem scope validation and symlink escape checks.
- `permissions/audit.py`: audit redaction and tamper-evident hash chain.
- `brain/dispatcher.py`: capability-first authorization before Agent execution.
- `agents/registry.py`: duplicate Agent registration protection.
- `agents/process_isolation.py`: subprocess timeout/termination foundation.
- `ui/secure_bridge.py`: local Unix socket bridge with launch token and origin
  verification.
- `core/events.py`: event-bus hardening.

## Modified File Links

- `permissions/engine.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py
- `permissions/registry.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/registry.py
- `permissions/audit.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/audit.py
- `permissions/confirmation.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/confirmation.py
- `permissions/scope.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/scope.py
- `brain/dispatcher.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/dispatcher.py
- `agents/process_isolation.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/agents/process_isolation.py
- `ui/secure_bridge.py`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/ui/secure_bridge.py
- `docs/sprint2_claude_findings_status.md`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/docs/sprint2_claude_findings_status.md
- `docs/safety_spine_verification_criteria.md`: https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/docs/safety_spine_verification_criteria.md

## Tests

Executed locally on `feature/NELA-safety-spine-routing`:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result:

- Language validation passed.
- 100 tests passed.
- UI headless smoke passed.

## Open Questions For Claude

- Is the current exact action tuple hash sufficient for P2, or should the tuple
  also include planner version / policy version?
- Should T1 filesystem actions require scoped sessions in addition to T2/T3 for
  early defense-in-depth?
- Is the current in-memory hash-chain audit model acceptable as a foundation if
  durable storage is explicitly blocked before advanced Agents?
- Should the WebView bridge expected origin be represented as a manifest setting
  when the production host is chosen?
- Are Terminal and Coding disabled capabilities documented clearly enough to
  avoid accidental enablement?

## Non-Goals Confirmed

- No merge requested yet.
- No Coding Agent implementation.
- No Cyber Agent implementation.
- No Browser/Vision expansion.
- No UI redesign.
- No direct Claude communication channel.
