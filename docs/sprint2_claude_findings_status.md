# Sprint 2 Claude Findings Status

Status: implementation status for `feature/NELA-safety-spine-routing`.

Claude reviewed the Sprint 2 design and raised ship-blocking findings. This
document maps each finding to the current code surface so Claude can review the
implementation directly.

## Status Summary

| ID | Finding | Current status |
| --- | --- | --- |
| A1 | WebView bridge authentication | Implemented foundation |
| K1 | Kill switch process isolation | Fixed for merge re-review |
| P1 | TOCTOU protection | Partially mitigated; deferred before write agents |
| P2 | Confirmation binding | Implemented |
| R1 | Agent registry overwrite | Fixed for merge re-review |
| L1 | Tamper-evident audit log | Partially implemented; durable default sink deferred |
| T1 | Authorization before final routing | Implemented foundation |
| T2 | Prompt injection into routing | Partially mitigated |

## A1 - WebView Bridge Authentication

Implemented in `ui/secure_bridge.py`.

- Uses a Unix domain socket, not TCP.
- Restricts socket filesystem permissions to `0600`.
- Uses a per-launch token.
- Verifies the expected origin.
- Does not expose `0.0.0.0`.
- Rejects requests without the launch token.
- Documents that backend permission checks remain authoritative.

Tests: `tests/test_secure_bridge.py`.

Remaining work: integrate this bridge only when the production WebView host is
selected. No unauthenticated WebView bridge should be merged.

## K1 - Kill Switch Process Isolation

Fixed for merge re-review in `agents/process_isolation.py` and
`brain/dispatcher.py`.

- Blocking work can run in a child process.
- Timeout terminates the process, then escalates to kill if needed.
- A `before_terminate` hook allows session revocation before termination.
- `ProcessOutcome.UNKNOWN` exists for child-process outcomes that cannot be
  safely classified.
- Dispatcher routes T2/T3 tasks and explicitly isolated tasks through
  `IsolatedAgentProcessRunner`.
- Active isolated workers track task ID, correlation ID, Agent ID, capability,
  and process ID.
- Kill switch activation cancels and terminates a blocked isolated worker.
- Scoped sessions are revoked before isolated emergency termination.
- Safe non-blocking T0/T1 tasks still execute directly.

Tests: `tests/test_process_isolation.py`, `tests/test_dispatcher.py`.

Remaining work: a full runtime supervisor and worker pool are future lifecycle
work. The before-merge K1 issue is fixed for current Dispatcher execution.

## P1 - TOCTOU Protection

Partially mitigated in `permissions/scope.py`.

- Filesystem paths are canonicalized with `Path.resolve`.
- Protected credential/security paths are denied.
- Scoped filesystem actions require an active scoped session.
- Symlink escape is denied by resolving the real target before authorization.
- Existing targets record stable `st_dev` / `st_ino` identity when available.
- Dispatcher calls permission authorization immediately before `agent.execute`.

Tests: `tests/test_permission_engine.py`.

Deferred requirement before enabling `coding.files.write`, `files.write`,
`files.move`, or `files.delete`: execution must enforce stable identity
(`st_dev`/`st_ino` or file descriptor equivalent), not only capture it.

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
- `replace()` requires explicit `ReplacementAuthorization`.
- `replace()` fails for missing Agents, self-replacement, manifest identity
  mismatch, version mismatch, and manifest fingerprint mismatch.
- Capability manifests reject duplicate registration by default.
- Capability manifest replacement is explicit through `replace_manifest()` and
  requires the expected manifest fingerprint.
- Ordinary registration paths do not call replacement implicitly.
- Registration attempts are recorded in registry audit trails.

Tests: `tests/test_agent_registry.py`, `tests/test_dispatcher.py`,
`tests/test_permission_engine.py`.

## L1 - Tamper-Evident Audit Log

Partially implemented in `permissions/audit.py`.

- Every record includes `previous_hash` and `entry_hash`.
- `AuditLog.verify_chain()` detects modification, deletion, and reordering.
- Sensitive fields are redacted before serialization.
- T2/T3 audit write failures fail closed in the Permission Engine.
- File-like durable sinks are flushed and `fsync`ed.

Tests: `tests/test_audit_log.py`, `tests/test_permission_engine.py`.

Deferred requirement before NELA 1.0 or durable T2/T3 workflows: default
persistent sink, startup chain verification, corruption detection, and
fail-closed behavior for corrupted durable audit state.

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
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
python3 -m core.app --once "נלה, תפתחי את Spotify" --no-dispatch
python3 -m unittest tests.test_agent_registry tests.test_dispatcher tests.test_process_isolation tests.test_permission_engine
python3 -m compileall permissions agents/process_isolation.py agents/registry.py brain/dispatcher.py brain/planner.py brain/conversation.py brain/decision.py brain/intent_router.py ui/secure_bridge.py tests
```

Result: 114 tests passed; dedicated K1/R1 tests passed; language pack validation passed; UI headless smoke
passed; Hebrew no-dispatch smoke produced `Intent: OpenApplication` and one
semantic launch task; compileall completed successfully.
