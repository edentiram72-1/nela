# NELA Sprint 2 PR Summary

Branch: `feature/NELA-safety-spine-routing`

Implementation commit verified before PR preparation: `11a2991`

Required-fix commit for Claude re-review: see final commit hash in handoff.

Base branch: `develop`

Status: Claude returned `APPROVE WITH REQUIRED FIXES`. K1/R1 required fixes are
implemented on this branch and need Claude re-review before merge.

## Sprint Goals

Sprint 2 builds the first production Safety Spine for NELA OS. The goal is to
make the Permission Engine the single gateway before every Agent execution while
keeping the Brain semantic, agent-neutral, and free of direct action logic.

This sprint does not implement Coding Agent, Cyber Agent, Browser Agent, Vision
Agent expansion, or advanced UI redesign.

## Features Implemented

- Permission tiers from `T0` through `T4`.
- Permission Engine authorization before `Agent.execute()`.
- Capability Registry and Agent manifests.
- Authentication foundation through `AuthenticatedUser`.
- User confirmation handling for `T2` and `T3`.
- Scoped sessions for future high-risk work.
- Audit log with tamper-evident hash chain.
- Kill switch.
- Lock mode.
- Event Bus hardening.
- Intelligent capability routing from semantic tasks to authorized Agents.
- Desktop Agent integration through semantic capabilities.
- Secure local UI bridge foundation for future WebView host.
- Subprocess isolation foundation for blocking or high-risk Agents.
- Dispatcher isolation policy for T2/T3 and explicitly isolated tasks.
- Kill Switch termination of blocked isolated workers.
- Protected Agent replacement with manifest fingerprint verification.

## Architecture Changes

The routing order is now:

```text
Intent
-> candidate capability set
-> policy eligibility
-> authorized candidate set
-> Agent selection
-> final scope validation
-> execution
```

The Planner emits semantic `Task.capability` values. The Dispatcher resolves
candidate Agents through the Capability Registry, authorizes each candidate, and
only then selects a concrete Agent.

The Brain still does not execute actions directly.

## Security Changes

- Unknown or undeclared actions fail closed.
- Disabled capabilities are denied.
- Duplicate Agent registration is rejected by default.
- T2/T3 confirmations are bound to exact action tuples.
- Filesystem scope validation canonicalizes paths and blocks protected targets.
- Audit records include `previous_hash` and `entry_hash`.
- T2/T3 audit write failures fail closed.
- Kill switch revokes scoped sessions before blocking non-read-only work.
- Future WebView bridge must use restricted local transport and launch tokens.
- T2/T3 and explicitly isolated Agent tasks use subprocess isolation.
- Safe non-blocking T0/T1 tasks remain direct by default.

## Permission Engine Summary

`permissions/engine.py` authorizes every proposed Agent command. It checks user
authentication, kill switch, lock mode, manifest-declared capability, disabled
capabilities, tier policy, confirmation binding, scoped sessions, and scope
validation before returning a grant.

## Capability Registry Summary

`permissions/registry.py` stores Agent manifests and resolves candidate Agents
for semantic capabilities. It is insert-only by default, validates manifest
identity and version, audits registration attempts, and rejects unsafe tier
downgrades.

## Agent Manifest Summary

Each manifest declares:

- Agent identity.
- Manifest version.
- Capability IDs.
- Supported actions.
- Permission tier.
- Optional platform constraints.
- Optional scopes.
- Optional confirmation requirement.

Terminal and Coding manifests include future declarations, but side-effecting
execution/write/commit capabilities are disabled.

## Audit Summary

`permissions/audit.py` provides structured audit records, metadata redaction,
query support, and hash-chain verification. The hash chain detects entry
modification, deletion, and reordering in the in-memory audit model.

Durable append-only storage remains future work.

## Kill Switch Summary

The kill switch blocks every non-`T0` action and revokes scoped sessions. Read-only
status checks may continue so NELA can still report state while locked down.

## Lock Mode Summary

Lock mode blocks every non-`T0` action while the system is locked. It is designed
for local runtime lockdown without shutting down the process.

## Event Bus Hardening Summary

The Event Bus now has bounded history, subscriber error isolation, event trace
metadata, and lifecycle events needed by the safety layer.

## Tests Executed

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result:

- Language validation passed.
- 114 tests passed.
- Dedicated K1/R1 tests passed (38 tests).
- UI headless smoke passed.

## Known Limitations

- Audit storage is still in-memory by default, though file-like sinks can be
  flushed and fsync'ed.
- Current safe low-risk T0/T1 Agent tasks are not moved into subprocesses by
  default.
- Full plugin manifest loading is not implemented yet.
- Parallel, conditional, cancellable, and async plan execution remain future
  work.
- WebView UI host selection is still future work.
- Terminal and Coding side-effecting capabilities remain disabled.
- Cyber capabilities remain blocked.

## Remaining Blockers

- Draft PR must be opened manually because GitHub CLI is not installed locally
  and prior connector attempts returned permission errors.
- 94 untracked duplicate-suffix local files still exist and are intentionally
  excluded from this PR.
- P1 stable identity enforcement is required before enabling file-writing
  capabilities.
- L1 durable audit storage and startup chain verification are required before
  NELA 1.0 or durable T2/T3 workflows.
- Task idempotency and production event-bus hardening are still required before
  advanced Agents gain real side effects.
