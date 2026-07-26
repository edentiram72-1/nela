# Claude Review — Open Findings Tracker

Single source of truth for every finding Claude has raised across NELA reviews,
with current status. Committed to the repo so review work is not stranded in
chat. Update the Status column as items close.

Legend: **OPEN** · **FIXED** · **PARTIAL** · **NOT REVIEWABLE** (code never seen)

Last updated against: Sprint 2 bundle commit `860fbd9`. Later commits
(`11a2991`, the `codex/nela-real-actions-cyber-learning` branch at `6196dd4`)
were **described but never delivered as code**, so their findings are marked
NOT REVIEWABLE until a bundle or blob links arrive.

---

## Safety Spine findings (from sprint2_architecture_review + verification)

| ID | Finding | Severity | Status @860fbd9 | Notes |
| --- | --- | --- | --- | --- |
| A1 | WebView bridge auth (Unix socket, token, origin) | CRIT | **FIXED (PASS)** | `ui/secure_bridge.py` — verify no GET side-effects once wired to a real handler |
| P2 | Confirmation bound to action-tuple hash | CRIT | **FIXED (PASS)** | `permissions/confirmation.py` |
| T1 | Tier from action, authorize after routing | CRIT | **FIXED (PASS)** | `permissions/engine.py::authorize` |
| T2 | Routing inputs structured, no content | CRIT | **FIXED (PASS)** | `find_agents_for_capability` |
| K1 | Subprocess isolation + kill switch | HIGH | **PARTIAL** | runner built; per status update now wired in `dispatcher._execute_agent` — RE-VERIFY `_requires_isolation` breadth + `unknown` outcome handling |
| R1 | Registry overwrite protection | MED | **PARTIAL** | `register()` insert-only, but `replace()`/`_store()` still `_agents.update()` with no guard — **fix supplied, not yet in delivered code** |
| P1 | TOCTOU: enforce captured st_dev/st_ino | HIGH | **PARTIAL** | identity captured, never enforced at execute. Gate for 1.0, before any file-writing agent |
| L1 | Audit hash-chain durable at rest | HIGH | **PARTIAL** | chain correct in-process; default `sink=None` ⇒ in-memory only, fsync path dead. Gate for 1.0 |

## Carried findings from earlier reviews

| ID | Finding | Status |
| --- | --- | --- |
| H3 | `StopTask`/`CloseApplication` require confirmation (inverted-safety) | **FIXED** @860fbd9 |
| NELA-0002-a | Confirmed intent re-plans from stored intent, not reply text | **FIXED** @860fbd9 |
| NELA-0002-b | Confirmation classifier exact-set match ("כן בבקשה" → unclear) | **OPEN** — MED |
| NELA-0002-c | "אל"/"stop" in negatives collide (safe under exact match only) | **OPEN** — LOW |
| X1 | Single pending-confirmation slot + single-use consumption | **OPEN** — MED, reachable once async execution lands |
| A3 | Scoped-session expiry on wall clock, not monotonic | **OPEN** — MED, before T3/lab |
| R3 | Agent manifest conformance tests | **OPEN** — track |
| M2 | Extract PlanExecutor from ConversationEngine | **OPEN** — track |

## Not-yet-reviewed (code never delivered)

| Area | Branch/commit | Status |
| --- | --- | --- |
| `11a2991` Safety Spine fixes | feature/NELA-safety-spine-routing | **NOT REVIEWABLE** |
| CyberDefenseAgent + defensive specialists | codex/nela-real-actions-cyber-learning @6196dd4 | **NOT REVIEWABLE** |
| Hebrew language-learning / real-action routing | same | **NOT REVIEWABLE** |
| Lock-mode voice bypass (A2) + locked-eye visual | voice/UI | **NOT REVIEWABLE** |

---

## Blocking status for merge into develop

**Before any merge that enables real agent actions:**
1. R1 `replace()` guard (fix written, must land + test).
2. K1 `_requires_isolation` verified to cover all T2/T3 + blocking actions;
   killed tasks record `unknown`, never `failed`.
3. **CyberDefenseAgent measured against the defensive-only bar** (next section) —
   this is the gate item for the current branch and cannot be waived on a
   description.

**Before NELA 1.0 (not blocking a docs/agent-scaffolding merge):**
4. P1 identity enforcement at execution.
5. L1 durable audit sink + startup chain verification.
6. A3 monotonic session expiry.

---

## Defensive-only acceptance bar for any cyber agent

Every cyber capability must satisfy ALL of these, verified from code:

1. Manifest declares only passive (T0/T1) or lab-only (T3) capabilities. No
   capability sends traffic to a target outside an isolated lab.
2. No external IP / hostname / URL is an acceptable target — rejected at scope
   validation as T4, with **no override flag**.
3. Ownership is structural (target exists inside the lab), never a user claim.
4. Output is findings + remediations + CVE/CWE references — never runnable
   exploit code.
5. "Educational" output explains a vulnerability class without supplying working
   attack tooling.
6. Every refusal is audited as loudly as every action.
7. Local scans (workspace/dependency/secrets/etc.) read only within declared
   filesystem scope; no scan writes to the audited system; no scan reaches the
   network.

A cyber capability that cannot be shown to meet all seven from its source is a
BLOCK, regardless of naming or stated intent.
