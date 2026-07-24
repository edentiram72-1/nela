# Sprint 2 Claude Findings Status

Status: implementation status for `feature/NELA-safety-spine-routing`.

Claude reviewed the Sprint 2 design and raised ship-blocking findings. This
document maps each finding to the current code surface so Claude can review the
implementation directly.

## Status Summary

| ID | Finding | Current status |
| --- | --- | --- |
| A1 | WebView bridge authentication | Implemented foundation |
| K1 | Kill switch process isolation | Implemented foundation |
| P1 | TOCTOU protection | Implemented foundation |
| P2 | Confirmation binding | Implemented |
| R1 | Agent registry overwrite | Implemented |
| L1 | Tamper-evident audit log | Implemented |
| T1 | Authorization before final routing | Implemented foundation |
| T2 | Prompt injection into routing | Partially mitigated |

## A1 - WebView Bridge Authentication

Implemented in `ui/secure_bridge.py`.

- Uses a Unix domain socket, not TCP.
- Uses a per-launch token.
- Verifies the expected origin.
- Does not expose `0.0.0.0`.
- Rejects requests without the launch token.
- Documents that backend permission checks remain authoritative.

Tests: `tests/test_secure_bridge.py`.

Remaining work: integrate this bridge only when the production WebView host is
selected. No unauthenticated WebView bridge should be merged.

## K1 - Kill Switch Process Isolation

Implemented foundation in `agents/process_isolation.py`.

- Blocking work can run in a child process.
- Timeout terminates the process, then escalates to kill if needed.
- A `before_terminate` hook allows session revocation before termination.

Tests: `tests/test_process_isolation.py`.

Remaining work: wire high-risk future Agents into this runner. Current live
Agents are not moved into subprocesses in this sprint.

## P1 - TOCTOU Protection

Implemented foundation in `permissions/scope.py`.

- Filesystem paths are canonicalized with `Path.resolve`.
- Protected credential/security paths are denied.
- Scoped filesystem actions require an active scoped session.
- Symlink escape is denied by resolving the real target before authorization.
- Dispatcher calls permission authorization immediately before `agent.execute`.

Tests: `tests/test_permission_engine.py`.

Remaining work: future file-writing Agents should execute against stable
verified objects or repeat scope checks at their own execution boundary.

## P2 - Confirmation Binding

Implemented in `permissions/confirmation.py`, `brain/conversation.py`,
`brain/planner.py`, and `permissions/engine.py`.

Every sensitive confirmation is bound to:

- Agent
- capability
- action
- target
- parameters
- session
- expiration

The Permission Engine recomputes the action tuple hash before authorizing T2/T3.
A confirmation for one action cannot be reused for another action.

Tests: `tests/test_permission_engine.py`, `tests/test_dispatcher.py`,
`tests/test_conversation_confirmations.py`.

## R1 - Agent Registry Overwrite

Implemented in `agents/registry.py` and `permissions/registry.py`.

- `AgentRegistry.register()` is insert-only by default.
- Duplicate Agent IDs raise `DuplicateAgentError`.
- `replace()` exists as an explicit replacement path.
- Capability manifests reject duplicate registration by default.
- Manifest identity and version are validated.
- Registration attempts are recorded in `CapabilityRegistry.registration_audit`.

Tests: `tests/test_dispatcher.py`, `tests/test_permission_engine.py`.

## L1 - Tamper-Evident Audit Log

Implemented in `permissions/audit.py`.

- Every record includes `previous_hash` and `entry_hash`.
- `AuditLog.verify_chain()` detects modification, deletion, and reordering.
- Sensitive fields are redacted before serialization.
- T2/T3 audit write failures fail closed in the Permission Engine.

Tests: `tests/test_audit_log.py`, `tests/test_permission_engine.py`.

Remaining work: durable disk persistence with fsync is still future work. The
current implementation is tamper-evident in memory and supports a sink for future
durable writes.

## T1 - Authorization Before Final Routing

Implemented foundation in `brain/dispatcher.py`, `brain/planner.py`, and
`permissions/registry.py`.

Current order:

```text
Intent
-> semantic Task capability
-> candidate Agents from Capability Registry
-> Permission Engine evaluation per candidate
-> authorized Agent selection
-> final scope validation
-> execution
```

User-facing commands no longer require the user to name internal Agents or
capabilities for normal app commands.

Tests: `tests/test_dispatcher.py`, `tests/test_planner.py`,
`tests/test_intent_recognition.py`, `tests/test_conversation_confirmations.py`.

Remaining work: full async/cancellable plan execution and plugin manifest
loading are future hardening work.

## T2 - Prompt Injection Into Routing

Partially mitigated.

- Routing now uses structured intent fields and semantic capabilities.
- Candidate Agents come from the Capability Registry, not free-form text.
- Unknown capability IDs deny by default.
- Application aliases are resolved from an allowlist in `brain/applications.py`.

Remaining work: future Research/Browser/Coding agents must ensure untrusted
content is never passed into router selection as authority. This should be
reviewed again before those agents gain real side effects.

## Validation

Latest local validation:

```text
python3 -m unittest discover -s tests
```

Result: 99 tests passed.
