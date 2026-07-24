# Claude Sprint 2 Review Bundle

Branch: `feature/NELA-safety-spine-routing`

Implementation review commit: `11a2991`

Required-fix commit for K1/R1 re-review: see final commit hash in handoff

Base branch: `develop`

Repository: `https://github.com/edentiram72-1/nela`

Compare URL:

```text
https://github.com/edentiram72-1/nela/compare/develop...feature/NELA-safety-spine-routing?expand=1
```

Required-fix branch tree:

```text
https://github.com/edentiram72-1/nela/tree/feature/NELA-safety-spine-routing
```

## Review Request

Claude returned `APPROVE WITH REQUIRED FIXES` for PR #2. Please re-review only
the before-merge fixes unless another regression is visible:

- K1: subprocess isolation is now wired into Dispatcher execution.
- R1: Agent Registry replacement bypass is now closed.

P1 and L1 remain documented deferred requirements before file-writing
capabilities, durable T2/T3 workflows, or NELA 1.0.

## Architecture Summary

Sprint 2 creates the first Safety Spine for NELA OS. The Brain remains
agent-neutral and does not perform external actions. It produces structured
intents and semantic tasks. The Dispatcher resolves candidate Agents through the
Capability Registry, asks the Permission Engine to authorize candidates, and
executes only after authorization succeeds.

Required order:

```text
Intent
-> candidate capability set
-> policy eligibility
-> authorized candidate set
-> Agent selection
-> final scope validation
-> execution
```

## Diff Summary Against `develop`

At the required-fix branch tip, the branch includes Sprint
2 Safety Spine code, K1/R1 required fixes, tests, and documentation. The major
runtime areas are:

- `permissions/`: Permission Engine, models, registry, audit, confirmation, and
  scope validation.
- `brain/`: semantic capability routing, confirmation continuation, and app
  alias handling.
- `agents/`: protected replacement and process isolation foundation.
- `brain/dispatcher.py`: isolated execution policy for T2/T3 and explicitly
  isolated tasks.
- `core/events.py`: hardened in-process Event Bus.
- `ui/secure_bridge.py`: secure local bridge foundation.
- `tests/`: permission, audit, dispatcher, Event Bus, confirmation, bridge, and
  process isolation coverage.

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
tests/test_agent_registry.py
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
- `permissions/models.py`: permission tiers, requests, decisions, capabilities,
  and manifests.
- `permissions/registry.py`: capability registry and manifest validation.
- `permissions/confirmation.py`: exact action tuple confirmation hash.
- `permissions/scope.py`: filesystem scope validation and symlink checks.
- `permissions/audit.py`: audit redaction and tamper-evident hash chain.
- `brain/dispatcher.py`: capability-first authorization before Agent execution
  plus isolated execution for T2/T3 and explicitly isolated tasks.
- `agents/registry.py`: duplicate Agent registration protection and protected
  manifest-bound replacement.
- `agents/process_isolation.py`: subprocess cancellation, timeout, and
  termination foundation.
- `ui/secure_bridge.py`: local Unix socket bridge with launch token and origin
  verification.
- `core/events.py`: Event Bus hardening.

## Permission Engine

Relevant files:

- `permissions/engine.py`
- `permissions/models.py`
- `tests/test_permission_engine.py`

Relevant implementation:

- `PermissionEngine.authorize()` at `permissions/engine.py:50`
- `PermissionEngine.record_action_result()` at `permissions/engine.py:172`
- `PermissionEngine.create_scoped_session()` at `permissions/engine.py:214`
- `PermissionEngine.activate_kill_switch()` at `permissions/engine.py:241`
- `PermissionEngine.set_lock_mode()` at `permissions/engine.py:263`
- `PermissionEngine._record()` at `permissions/engine.py:324`
- `PermissionEngine._confirmation_error()` at `permissions/engine.py:380`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L25
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/models.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_permission_engine.py

## Capability Registry And Agent Manifests

Relevant files:

- `permissions/registry.py`
- `permissions/models.py`
- `agents/registry.py`
- `tests/test_permission_engine.py`
- `tests/test_dispatcher.py`

Relevant implementation:

- `CapabilityRegistry.register_manifest()` at `permissions/registry.py:49`
- `CapabilityRegistry.find_agents_for_capability()` at `permissions/registry.py:85`
- `CapabilityRegistry.validate_manifest()` at `permissions/registry.py:104`
- `MINIMUM_CAPABILITY_TIERS` at `permissions/registry.py:21`
- `AgentRegistry.register()` at `agents/registry.py:19`
- `AgentRegistry.replace()` at `agents/registry.py:25`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/registry.py#L39
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/agents/registry.py#L8

## Confirmation Token Implementation

Relevant files:

- `permissions/confirmation.py`
- `permissions/engine.py`
- `brain/conversation.py`
- `brain/planner.py`
- `tests/test_permission_engine.py`
- `tests/test_conversation_confirmations.py`

Relevant implementation:

- `action_tuple_hash()` at `permissions/confirmation.py:25`
- Confirmation validation in `PermissionEngine._confirmation_error()` at
  `permissions/engine.py:380`
- Dispatcher passes confirmation hash/expiration through `PermissionRequest` at
  `brain/dispatcher.py:231`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/confirmation.py#L25
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L380

## Authentication And Scoped Sessions

Relevant files:

- `permissions/models.py`
- `permissions/engine.py`
- `tests/test_permission_engine.py`

Relevant implementation:

- `AuthenticatedUser`, `ScopedSession`, and `PermissionRequest` in
  `permissions/models.py`
- `PermissionEngine.create_scoped_session()` at `permissions/engine.py:214`
- Scoped-session revocation in `PermissionEngine.activate_kill_switch()` at
  `permissions/engine.py:241`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/models.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L214

## Audit Hash Chain

Relevant files:

- `permissions/audit.py`
- `tests/test_audit_log.py`
- `tests/test_permission_engine.py`

Relevant implementation:

- `AuditLog.append()` at `permissions/audit.py:113`
- `AuditLog.verify_chain()` at `permissions/audit.py:166`
- `entry_hash()` at `permissions/audit.py:197`
- `previous_hash` and `entry_hash` fields at `permissions/audit.py:59`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/audit.py#L102
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_audit_log.py

## Kill Switch

Relevant files:

- `permissions/engine.py`
- `tests/test_permission_engine.py`

Relevant implementation:

- `PermissionEngine.activate_kill_switch()` at `permissions/engine.py:241`
- `PermissionEngine.deactivate_kill_switch()` near the same section
- Scoped-session revocation before non-read-only shutdown behavior

Evidence link:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L241

## Lock Mode

Relevant files:

- `permissions/engine.py`
- `tests/test_permission_engine.py`

Relevant implementation:

- `PermissionEngine.set_lock_mode()` at `permissions/engine.py:263`

Evidence link:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L263

## Event Bus Hardening

Relevant files:

- `core/events.py`
- `tests/test_events.py`

Relevant implementation:

- `EventBus` at `core/events.py:72`
- bounded history at `core/events.py:77`
- subscriber isolation in `_call_handler()` at `core/events.py:123`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/core/events.py#L72
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_events.py

## WebView Bridge Security

Relevant files:

- `ui/secure_bridge.py`
- `tests/test_secure_bridge.py`

Relevant implementation:

- `SecureLocalBridge` at `ui/secure_bridge.py:23`
- expected origin at `ui/secure_bridge.py:31`
- Unix domain socket at `ui/secure_bridge.py:40`
- token/origin validation at `ui/secure_bridge.py:50`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/ui/secure_bridge.py#L23
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_secure_bridge.py

## Worker Process Isolation

Relevant files:

- `agents/process_isolation.py`
- `brain/dispatcher.py`
- `tests/test_process_isolation.py`
- `tests/test_dispatcher.py`

Relevant implementation:

- `IsolatedAgentProcessRunner` at `agents/process_isolation.py:29`
- timeout termination flow at `agents/process_isolation.py:40`
- `before_terminate` hook at `agents/process_isolation.py:46`
- terminate/kill escalation at `agents/process_isolation.py:48`
- Dispatcher isolated execution policy in `brain/dispatcher.py`
- Active worker tracking in `brain/dispatcher.py`
- Kill-switch cancellation check in `brain/dispatcher.py`

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/agents/process_isolation.py#L29
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_process_isolation.py

## Routing Trust Boundary

Relevant files:

- `brain/dispatcher.py`
- `brain/planner.py`
- `brain/intent_router.py`
- `brain/applications.py`
- `permissions/registry.py`
- `tests/test_dispatcher.py`
- `tests/test_intent_recognition.py`
- `tests/test_planner.py`

Relevant implementation:

- Dispatcher passes confirmation hash/expiration in requests at
  `brain/dispatcher.py:231`
- Permission denial handling in `brain/dispatcher.py:255`
- Planner emits semantic task capabilities.
- Application aliases are allowlist-resolved in `brain/applications.py`.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/dispatcher.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/applications.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_dispatcher.py

## Finding A1 - WebView Bridge Authentication

Relevant files:

- `ui/secure_bridge.py`
- `tests/test_secure_bridge.py`

Relevant functions/classes:

- `SecureLocalBridge`
- `SecureLocalBridge.start()`
- `SecureLocalBridge.authorize_request()`

Implementation summary:

- The bridge foundation uses a Unix domain socket instead of TCP.
- It generates a per-launch token.
- It validates expected origin and token.
- It does not bind to `0.0.0.0`.
- The UI client remains non-authoritative; Agent execution still requires
  backend Permission Engine approval.

Tests covering the finding:

- `tests/test_secure_bridge.py`

Unresolved questions:

- The production WebView host is not selected yet, so host integration remains
  future work.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/ui/secure_bridge.py#L23
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_secure_bridge.py

## Finding K1 - Subprocess Isolation And Kill Switch

Relevant files:

- `agents/process_isolation.py`
- `brain/dispatcher.py`
- `permissions/engine.py`
- `tests/test_process_isolation.py`
- `tests/test_dispatcher.py`
- `tests/test_permission_engine.py`

Relevant functions/classes:

- `IsolatedAgentProcessRunner`
- `AgentDispatcher._requires_isolation()`
- `AgentDispatcher._execute_agent()`
- `AgentDispatcher.active_workers()`
- `PermissionEngine.activate_kill_switch()`

Implementation summary:

- Dispatcher routes T2/T3 tasks and explicitly isolated tasks through
  `IsolatedAgentProcessRunner`.
- Safe non-blocking T0/T1 tasks still execute directly by default.
- Active workers track task ID, correlation ID, Agent ID, capability, and
  process ID.
- Timeout calls `before_terminate`, then terminates and can kill the child.
- Kill switch cancellation is checked while the child process is running.
- Kill switch revokes scoped sessions, cancels the blocked isolated worker, and
  prevents new non-T0 dispatches.
- Timeout, cancellation, worker crash, and unknown outcomes return structured
  failed `AgentResult` objects.
- Execution results and cancellation/termination failures are preserved in the
  audit log.

Tests covering the finding:

- `tests/test_process_isolation.py`
- K1 isolated-dispatch tests in `tests/test_dispatcher.py`
- kill-switch tests in `tests/test_permission_engine.py`

Unresolved questions:

- Runtime-wide worker pool/supervisor remains future lifecycle work. The
  before-merge K1 Dispatcher wiring issue is fixed.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/agents/process_isolation.py#L29
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/dispatcher.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L241

## Finding P1 - TOCTOU Protection

Relevant files:

- `permissions/scope.py`
- `permissions/engine.py`
- `brain/dispatcher.py`
- `tests/test_permission_engine.py`

Relevant functions/classes:

- `validate_scopes()`
- `validate_filesystem_scope()`
- `PermissionEngine.authorize()`

Implementation summary:

- Filesystem paths are canonicalized with `Path.resolve`.
- Protected credential/security paths are denied.
- Symlink escape is denied during permission evaluation.
- Dispatcher authorizes immediately before calling `Agent.execute()`.

Tests covering the finding:

- symlink escape and scope-denial tests in `tests/test_permission_engine.py`

Unresolved questions:

- Future file-writing Agents should bind authorization to stable file handles or
  repeat validation at their own execution boundary.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/scope.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/dispatcher.py

## Finding P2 - Confirmation Binding

Relevant files:

- `permissions/confirmation.py`
- `permissions/engine.py`
- `brain/conversation.py`
- `brain/planner.py`
- `tests/test_permission_engine.py`
- `tests/test_conversation_confirmations.py`

Relevant functions/classes:

- `action_tuple_hash()`
- `PermissionEngine._confirmation_error()`

Implementation summary:

- Confirmation token is bound to Agent, capability, action, target, parameters,
  session, and expiration.
- Permission Engine recomputes the tuple hash before authorizing T2/T3.
- Expired or mismatched confirmation data is denied.

Tests covering the finding:

- confirmation mismatch/expiry tests in `tests/test_permission_engine.py`
- multi-turn confirmation tests in `tests/test_conversation_confirmations.py`

Unresolved questions:

- Claude should decide whether policy version or planner version must also be
  included in the hash tuple.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/confirmation.py#L25
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/engine.py#L380

## Finding R1 - Agent Registry Overwrite Protection

Relevant files:

- `agents/registry.py`
- `permissions/registry.py`
- `permissions/models.py`
- `tests/test_agent_registry.py`
- `tests/test_dispatcher.py`
- `tests/test_permission_engine.py`

Relevant functions/classes:

- `AgentRegistry.register()`
- `AgentRegistry.replace()`
- `ReplacementAuthorization`
- `authorize_replacement()`
- `CapabilityRegistry.register_manifest()`
- `CapabilityRegistry.replace_manifest()`
- `manifest_fingerprint()`

Implementation summary:

- Runtime Agent registration rejects duplicate names by default.
- Replacement requires explicit `ReplacementAuthorization` bound to Agent ID,
  manifest version, and manifest fingerprint.
- Replacement fails for missing Agents, self-replacement, missing
  authorization, manifest identity mismatch, authorization identity mismatch,
  and fingerprint mismatch.
- Direct `_store()` calls cannot silently overwrite an existing Agent unless the
  protected replacement path has already validated the request.
- Capability manifest registration rejects duplicates by default.
- Capability manifest replacement requires explicit `replace_manifest()` with
  matching fingerprint.
- Ordinary registration paths never call replacement implicitly.
- Registration and replacement attempts are audited in registry state.

Tests covering the finding:

- replacement-bypass tests in `tests/test_agent_registry.py`
- duplicate Agent and duplicate manifest tests in `tests/test_dispatcher.py` and
  `tests/test_permission_engine.py`

Unresolved questions:

- Future plugin loader should define a signed or trusted external replacement
  policy. The current local replacement API is protected and explicit.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/agents/registry.py#L8
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/registry.py#L39

## Finding L1 - Audit Hash-Chain Integrity

Relevant files:

- `permissions/audit.py`
- `permissions/engine.py`
- `tests/test_audit_log.py`
- `tests/test_permission_engine.py`

Relevant functions/classes:

- `AuditLog.append()`
- `AuditLog.verify_chain()`
- `entry_hash()`
- `PermissionEngine._record()`

Implementation summary:

- Every audit entry stores previous and current entry hashes.
- Verification detects mutation, deletion, and reordering.
- Sensitive metadata is redacted.
- T2/T3 audit write failures fail closed.

Tests covering the finding:

- tamper/deletion/reorder tests in `tests/test_audit_log.py`
- fail-closed audit tests in `tests/test_permission_engine.py`

Unresolved questions:

- Durable append-only storage with fsync semantics is future work.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/audit.py#L102
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_audit_log.py

## Finding T1 - Authorization-Safe Routing

Relevant files:

- `brain/dispatcher.py`
- `brain/planner.py`
- `permissions/registry.py`
- `tests/test_dispatcher.py`
- `tests/test_planner.py`

Relevant functions/classes:

- `AgentDispatcher.dispatch()`
- Dispatcher permission request builder.
- `CapabilityRegistry.find_agents_for_capability()`

Implementation summary:

- Planner emits semantic capabilities.
- Dispatcher builds candidate Agents from registry capabilities.
- Permission Engine evaluates candidates before Agent selection.
- Agent execution is skipped when authorization fails.

Tests covering the finding:

- capability routing tests in `tests/test_dispatcher.py`
- semantic capability planning tests in `tests/test_planner.py`

Unresolved questions:

- Full async/cancellable plan execution remains future work.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/dispatcher.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/permissions/registry.py#L85

## Finding T2 - Prompt-Injection-Resistant Routing

Relevant files:

- `brain/intent_router.py`
- `brain/applications.py`
- `brain/planner.py`
- `brain/dispatcher.py`
- `permissions/registry.py`
- `tests/test_intent_recognition.py`
- `tests/test_dispatcher.py`

Relevant functions/classes:

- `IntentRouter`
- `resolve_application_alias()`
- semantic `Task.capability`
- `CapabilityRegistry.find_agents_for_capability()`

Implementation summary:

- User text is converted into structured intent fields.
- Application names use an allowlist resolver.
- Agent selection uses manifest-declared capabilities, not raw user text.
- Unknown capabilities and actions deny by default.
- Terminal and Coding side-effecting declarations remain disabled.

Tests covering the finding:

- Hebrew alias tests in `tests/test_intent_recognition.py`
- routing tests in `tests/test_dispatcher.py`

Unresolved questions:

- Future Browser/Research/Coding agents must prevent untrusted content from
  becoming routing authority.

Evidence links:

- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/applications.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/brain/dispatcher.py
- https://github.com/edentiram72-1/nela/blob/feature/NELA-safety-spine-routing/tests/test_intent_recognition.py

## Relevant Tests

Executed locally before package finalization:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
python3 -m unittest tests.test_agent_registry tests.test_dispatcher tests.test_process_isolation tests.test_permission_engine
python3 -m compileall agents/process_isolation.py agents/registry.py brain/dispatcher.py permissions tests/test_agent_registry.py tests/test_dispatcher.py tests/test_permission_engine.py tests/test_process_isolation.py
```

Result:

- Language validation passed.
- 114 tests passed.
- Dedicated K1/R1 tests passed (38 tests).
- UI headless smoke passed.
- Hebrew no-dispatch smoke passed.
- Compileall completed successfully.

## Current Limitations

- P1 stable identity enforcement is still required before enabling
  `coding.files.write`, `files.write`, `files.move`, or `files.delete`.
- L1 default persistent audit sink, startup chain verification, corruption
  detection, and durable fail-closed behavior are required before NELA 1.0 or
  durable T2/T3 workflows.
- Safe non-blocking T0/T1 tasks are intentionally not isolated by default.
- WebView host integration is future work.
- Plugin manifest loading is not implemented.
- Terminal and Coding side-effecting capabilities are disabled declarations.
- Cyber capabilities remain blocked.
- Full async/cancellable plan execution is future work.
- 94 local duplicate-suffix files remain untracked and intentionally excluded.

## Open Questions For Claude

- Should confirmation hashes include policy version or planner version?
- Should T1 filesystem work require scoped sessions?
- Is the in-memory audit hash-chain acceptable as a foundation if durable audit
  is explicitly required before advanced Agents?
- Should WebView bridge origin be represented in a host manifest?
- Are disabled Terminal/Coding capabilities documented clearly enough to prevent
  accidental enablement?
