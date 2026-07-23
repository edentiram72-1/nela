# Permission Engine Implementation

Status: implemented in Sprint 2 on `feature/NELA-sprint-2-permission-engine`.

The Permission Engine is the single gateway before every Agent execution. The
Brain still thinks, plans, remembers, and delegates; it does not execute actions
and it does not contain Agent-specific permission logic.

## Purpose

The engine converts a proposed Agent command into an authorization decision:

```text
Task -> Dispatcher -> PermissionEngine -> Agent.execute()
```

If authorization fails, the Agent is not called.

## Implemented Components

### Permission Tiers

`permissions.models.PermissionTier` defines:

- `T0`: read-only
- `T1`: safe local action
- `T2`: user confirmation required
- `T3`: scoped high-risk lab/session action
- `T4`: forbidden

Unknown or undeclared actions fail closed as `T4`.

### Capability Registry

`permissions.registry.CapabilityRegistry` stores `AgentManifest` objects. Each
manifest declares the actions an Agent is allowed to expose.

Built-in manifests currently exist for:

- `desktop`
- `voice`
- `memory`
- `spotify`
- current placeholder Agents with read-only status/health capabilities

Dynamic Agents can provide a `permission_manifest` attribute. If an Agent has no
manifest and no built-in baseline, it registers with no executable actions.

### Agent Manifests

An Agent manifest contains:

- Agent name
- Manifest version
- Declared capabilities
- Capability tier
- Optional scopes
- Optional confirmation requirement

Example:

```python
AgentManifest(
    agent="desktop",
    capabilities=(
        Capability("launch_application", PermissionTier.T1),
        Capability("close_application", PermissionTier.T2, requires_confirmation=True),
    ),
)
```

### Authentication

The engine accepts an `AuthenticatedUser` on each `PermissionRequest`. The
current runtime uses a local authenticated owner context by default. Requests
from unauthenticated users are denied before scope or tier checks.

### User Confirmation

`T2` and `T3` actions require `confirmed=True` in the request. The existing
conversation confirmation flow sets this flag after the user confirms a pending
request. `CloseApplication` now carries this confirmation flag into the desktop
task payload.

The Permission Engine does not ask the user directly. It emits
`PermissionRequested` and returns `confirmation_required`. Conversation-level
confirmation remains owned by the existing Brain flow.

### Scoped Sessions

`ScopedSession` provides a time-limited authorization boundary for higher-risk
future work. In Sprint 2 it supports:

- allowed Agents
- allowed tiers
- named scope grants
- expiry
- revocation

`T3` requires an active scoped session plus confirmation.

### Audit Log

`AuditLog` is append-only and in-memory for Sprint 2. It records:

- authorization grants
- denials
- confirmation requirements
- scope violations
- action execution results

A durable audit writer can replace this later without changing the Dispatcher
integration.

### Kill Switch

`PermissionEngine.activate_kill_switch()` blocks every non-`T0` action. Read-only
status checks can still proceed. The engine emits `KillSwitchActivated` and
`KillSwitchDeactivated`.

### Lock Mode

`PermissionEngine.set_lock_mode(True)` blocks every non-`T0` action while the
system is locked. It emits `LockModeChanged`.

## Event Contract

Sprint 2 adds these EventTypes:

- `PermissionRequested`
- `PermissionGranted`
- `PermissionDenied`
- `ScopeViolation`
- `ActionExecuted`
- `ActionRolledBack`
- `KillSwitchActivated`
- `KillSwitchDeactivated`
- `LockModeChanged`

The UI event bridge maps permission waiting and denial events to existing Eye
states without redesigning the UI.

## Dispatcher Integration

`AgentDispatcher.dispatch()` now:

1. Resolves the target Agent.
2. Builds a `PermissionRequest`.
3. Calls `PermissionEngine.authorize()`.
4. Stops before `Agent.execute()` if authorization fails.
5. Uses the permission request `command_id` as the `AgentCommand.id`.
6. Records the Agent result in the audit log after execution.

This keeps authorization centralized and avoids Agent-specific logic in the
Brain.

## Current Limits

- Audit storage is in-memory only.
- Scope validation is intentionally minimal until real scoped Agents exist.
- `ActionRolledBack` is declared but rollback execution is future work.
- Kill switch currently blocks future execution; full cancellation of in-flight
  blocking Agent calls remains part of future runtime hardening.
- No Coding Agent or Cyber Agent was implemented in this sprint.

## Validation

```text
python3 -m unittest discover -s tests
```

Result: 76 tests passed.

Additional smoke checks:

```text
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
python3 -m compileall permissions brain/dispatcher.py brain/planner.py core/events.py ui/events.py tests/test_permission_engine.py tests/test_dispatcher.py tests/test_conversation_confirmations.py
```

Result: all passed.
