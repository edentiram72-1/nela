# Audit Log And Recovery

Status: implemented foundation on `feature/NELA-safety-spine-routing`.

## Purpose

The audit layer records important permission and execution decisions so future
Assistants can inspect what happened and why. It is part of the Safety Spine,
not an optional debug log.

## Audit Records

`permissions.audit.AuditRecord` captures:

- Event type.
- Decision or outcome.
- Agent.
- Capability.
- Action.
- Target.
- User.
- Session.
- Redacted metadata.
- Previous entry hash.
- Current entry hash.

## Tamper Evidence

Every entry is linked to the previous entry hash. `AuditLog.verify_chain()`
detects modification, deletion, and reordering inside the recorded chain.

This is not yet durable storage. It is the in-memory model and validation
contract that durable storage must preserve.

## Fail-Closed Rules

For `T2` and `T3`, a required audit write failure denies execution. NELA must not
perform sensitive work that cannot be recorded.

For `T0` and `T1`, the current engine can continue while logging the write
failure in the decision reason, because these tiers are intended to be read-only
or low-risk local actions.

## Redaction

Known sensitive keys and token-like values are redacted before serialization.
Future durable sinks should write only the redacted form.

## Recovery Hooks

Current recovery support:

- Kill switch revokes scoped sessions.
- Lock mode blocks non-read-only work.
- Process isolation foundation can revoke sessions before terminating a blocked
  child process.

Future work:

- Durable append-only audit store with fsync semantics.
- Rollback handlers for actions that support reversal.
- Correlation IDs across plans, tasks, events, and audit records.
