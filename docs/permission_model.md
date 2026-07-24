# NELA Permission & Approval Model

This is the **spine** of NELA's agent system. Every action any agent takes is
classified into exactly one capability tier, and the tier decides what happens
before, during, and after. No agent implements its own safety rules — they all
call the same engine described here.

Status: Sprint 2 implementation exists in `permissions/`; this document remains
the long-term policy model. See `docs/permission_engine.md` for the implemented
runtime surface and current limits.

Related: `permission_model` was flagged as required-before-real-agents in
`docs/claude_review_findings.md` (H3) and is a hard prerequisite for every
agent in `coding_agent_spec.md` and `cyber_agent_spec.md`.

---

## 1. Capability tiers

Five tiers, ordered by blast radius. Every agent action declares its tier
statically (in its capability manifest — see §4); the engine never infers it.

| Tier | Name | Meaning | Gate |
| --- | --- | --- | --- |
| T0 | **Read-only** | Observes, never changes state. Read files, list processes, fetch a URL, inspect a repo, read logs. | none (still logged) |
| T1 | **Safe local** | Reversible local changes with no external effect. Write to a scratch dir, format code, create a branch, stage changes. | none (logged + rollback token) |
| T2 | **Confirmation required** | Real side effects, reversible-with-effort. Commit, push to a non-protected branch, close an app, send a PR, install a dependency, write outside scratch. | user confirmation (reuses NELA-0002 flow) |
| T3 | **High-risk / isolated lab only** | Actions permitted **only** inside the sandboxed Cyber Lab (`cyber_agent_spec.md` §4). Active vulnerability scanning, exploit validation against user-owned lab targets, destructive test fixtures. | explicit per-session lab authorization + scope token + confirmation |
| T4 | **Forbidden** | Never executed by any agent under any framing. | hard refusal |

### T4 — forbidden (non-exhaustive, deny-by-default)

- Force-kill, `rm -rf` outside scratch, disk formatting, privilege escalation.
- Any network action against a target not in the authorized scope list.
- Offensive security actions against third parties: scanning, exploiting, or
  DoSing systems the user does not own and has not proven authorization for.
- Exfiltrating secrets, disabling the audit log, or modifying the permission
  engine itself.
- Committing secrets, weakening security controls, or bypassing another
  agent's required confirmation.

Deny-by-default is literal: an action whose tier cannot be determined is
treated as T4.

## 2. The approval flow

```text
agent proposes action
      │
      ▼
┌─────────────────┐   T4 → refuse + AuditLog(refused) + notify
│ classify tier   │
└────────┬────────┘
         │ T0/T1/T2/T3
         ▼
┌─────────────────┐   fail → refuse (out-of-scope target, unknown tool)
│ scope validation│
└────────┬────────┘
         ▼
┌─────────────────┐   T2 → user confirm (NELA-0002 flow)
│ gate for tier   │   T3 → lab auth + scope token + confirm
└────────┬────────┘   T0/T1 → pass
         ▼
┌─────────────────┐
│ pre-image snap  │   (T1+ capture rollback token)
└────────┬────────┘
         ▼
      execute  ── rate-limited, sandboxed per tier
         │
         ▼
┌─────────────────┐
│ AuditLog(result)│   + rollback token stored
└─────────────────┘
```

Every branch emits an event: `PermissionRequested`, `PermissionGranted`,
`PermissionDenied`, `ScopeViolation`, `ActionExecuted`, `ActionRolledBack`.
These extend the existing `EventTypes`; the eye's `waiting` state is the face
of `PermissionRequested`.

## 3. Scope validation

Before any T2+ action, the engine checks the action's **target** against an
explicit scope:

- **Filesystem scope:** an allowlist of roots the agent may touch (project
  dir, scratch dir). Paths are canonicalized (`realpath`) before the check, so
  `../` traversal and symlink escapes fail closed.
- **Network scope:** an allowlist of hosts/CIDRs. Empty by default. Cyber Lab
  targets must be user-owned and listed with a proof-of-ownership record
  (`cyber_agent_spec.md` §3).
- **Repo scope:** which repos/branches an agent may write. Protected branches
  (`main`, `release/*`) are never in a coding agent's write scope — it opens
  PRs instead.

A scope token is a signed, time-boxed grant naming (agent, tier, targets,
expiry). T3 actions require a fresh token per session; tokens are single-scope
and non-transferable between agents.

## 4. Agent capability manifest

Every agent ships a static manifest the engine loads at registration. No
action outside the manifest is executable — this is how a new agent is made
safe by construction:

```yaml
agent: coding
version: 1
capabilities:
  - action: read_repo            tier: T0
  - action: run_tests            tier: T1   sandbox: subprocess
  - action: edit_file            tier: T1   scope: [filesystem.project]
  - action: create_branch        tier: T1
  - action: commit               tier: T2
  - action: push_branch          tier: T2   scope: [repo.non_protected]
  - action: open_pull_request    tier: T2
  - action: install_dependency   tier: T2   sandbox: subprocess
forbidden:
  - push to protected branch
  - edit outside filesystem.project
```

The dispatcher refuses to route a task whose action is not in the target
agent's manifest — this also closes the capability-registry gap from the Phase
1 review (H1).

## 5. Cross-cutting controls

### Audit trail
Append-only log (`audit_agent_spec` below is folded in here). Every action —
including T0 reads and every refusal — writes a record: `{ts, agent, action,
tier, target, scope_token, decision, result, rollback_token, correlation_id}`.
The log is not writable by agents (T4 to modify it). `correlation_id` ties an
action back to the conversation turn that spawned it.

### Kill switch
A single global stop that (a) cancels all in-flight tasks via the existing
`cancel_task` path, (b) revokes all active scope tokens, (c) drops every agent
to T0. Triggerable by the user (UI + a hardware-independent hotkey), by the
runtime on anomaly (rate-limit breach, repeated scope violations), and
programmatically by the audit monitor. The eye goes to a dedicated
locked-`offline` visual so the halt is unmistakable.

### Sandboxing (per tier)
- T1 test/format runs: subprocess with no network, CPU/mem/time limits,
  writes confined to scratch.
- T3 lab: full network+filesystem isolation (VM or container), no route to the
  host or the internet except explicitly listed lab targets. Detailed in
  `cyber_agent_spec.md` §4.

### Rate limits
Per-agent, per-tier token buckets. T2 confirmations are also rate-limited to
prevent confirmation-fatigue attacks (an agent spamming approvals until the
user reflexively accepts). Breach → kill switch + `AnomalyDetected`.

### Secrets & credentials
- Secrets live in the OS keychain, never in files, memory dumps, logs, or the
  audit trail (the logger redacts on a secret-pattern match).
- Agents receive **capabilities, not secrets**: e.g. the Git agent gets a
  scoped, short-lived token minted per operation, never the raw PAT.
- A secret detected in proposed committed content is a T4 hard block (this is
  also a coding-agent pre-commit check).
- Secret access is itself audited (which agent, which secret handle, when).

### Rollback
- T1/T2 file actions capture a pre-image (git stash / content snapshot) →
  `rollback_token`. `ActionRolledBack` restores it.
- Git actions prefer reversible forms: new branches over force-push, revert
  commits over history rewrites, PRs over direct merges.
- The kill switch offers "roll back last N actions" using stored tokens.

## 6. Interaction with existing systems

- **Brain:** unchanged. The dispatcher gains one call — `permission.authorize
  (agent, action, target)` — before `agent.execute`. Denials become
  `TaskFailed` with reason.
- **Memory:** scope grants, ownership proofs, and the rolling audit summary
  are project-scoped memory (`memory/` subsystem). The permission engine
  reads `relationship_stage`/trust never — trust does not relax tiers.
- **Confirmation:** T2/T3 reuse the exact NELA-0002 machinery; no second
  confirmation system.

## 7. Non-negotiables

1. Tiers are declared, never inferred; undetermined ⇒ T4.
2. Trust/relationship level never lowers a tier.
3. The audit log and the permission engine are unmodifiable by agents.
4. Offensive action against non-owned targets is T4, full stop.
5. Every refusal is logged as loudly as every action.
