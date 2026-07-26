# Runtime Operations

Operational depth for the NELA Runtime: lifecycle, queue mechanics, recovery,
health monitoring, and resource management. Extends
`nela_runtime_architecture.md` with the behaviours that matter once agents run
concurrently and NELA stays up for days.

Companion: `multi_agent_orchestration.md`, `sprint2_architecture_review.md`
(findings K1–K4, X1–X3).

---

## 1. Runtime lifecycle

```text
boot → verify → construct → register → ready ⇄ degraded
                                          │        │
                                       locked   quarantine-heavy
                                          │
                                    killed → recovery (explicit) → ready
```

**Boot-time verification (fail closed on any failure):**
1. Audit chain intact from the last shutdown (verify terminal hash).
2. Policy and manifests parse, versions known, hashes match pins.
3. Manifest paths resolve **outside** every agent-writable scope (review P3).
4. Bridge binds to the intended socket/loopback only — a non-loopback bind
   aborts startup.
5. Secrets broker reachable; no plaintext credential fallback exists.

Any failure ⇒ start in **degraded mode**: T0 only, user notified, reason
audited. NELA that cannot audit must not act.

**Shutdown:** drain the queue (or checkpoint it), flush audit buffers with
fsync, write a terminal chain hash, revoke sessions, destroy elevation (never
persisted), tear down any lab.

## 2. Agent lifecycle

States extend the existing `AgentState`:

```text
registered → ready ⇄ running ⇄ sleeping
                │        │
                └──── quarantined ──(explicit, audited)──> ready
                          ▲
        health failure ───┤
        rate-limit breach ┤
        scope violation ──┘
```

- **Registration** is insert-only; duplicates raise (review R1). Requires a
  valid manifest *and* passing conformance tests (review R3).
- **Sleeping** releases resources after idle; resume is lazy on first task.
- **Quarantine** is the containment primitive: no tasks routed, excluded from
  routing candidates, user-visible, audited. Recovery is explicit and never
  automatic — an agent that quarantines itself repeatedly is a defect, and
  auto-recovery hides it.
- **Deregistration** during flight: in-flight tasks complete or are abandoned
  per §5; the registry uses copy-on-write snapshots so dispatch never iterates
  a mutating map (review R4).

## 3. Task queue

Priority queue owned by the Runtime; dependency-aware; concurrency-bounded.

**Eligibility:** all `depends_on` completed, agent available, session alive,
scope free.

**Serialization rules (non-negotiable):**
1. Tasks sharing a filesystem scope run serially — no write races.
2. **At most one pending confirmation system-wide** (review X1). Other tasks
   needing confirmation wait in the queue rather than opening parallel
   questions. Assert this invariant; it is currently only assumed.
3. Rollback within a scope is strictly LIFO (review X2).

**Backpressure:** the queue is bounded. When full, new tasks are rejected with
an honest message rather than growing memory. Priority does not bypass the
bound; it reorders within it.

**Starvation:** low-priority tasks age upward so a stream of urgent work cannot
starve them indefinitely.

**Persistence:** the queue is checkpointed so a restart does not silently lose
accepted work. Checkpointed tasks are re-authorized on resume — never resumed
under a dead session's grants.

## 4. Concurrency and isolation

- Agent actions that can block on external I/O run in **subprocess** workers,
  not threads. This is the only way timeouts and the kill switch can actually
  interrupt work in Python (review K1). Threads remain acceptable for pure
  in-memory work.
- Workers get resource limits: CPU time, memory, wall clock, no network unless
  the action's scope grants it.
- Concurrency is configurable down to 1, which reproduces today's sequential
  behaviour — the safe fallback if concurrency misbehaves.

## 5. Outcomes, including the honest one

Three terminal states, not two:

| Outcome | Meaning | Retry policy |
| --- | --- | --- |
| `completed` | verified success | n/a |
| `failed` | verified not done | retry only if idempotent + transient |
| `unknown` | killed, timed out, or abandoned mid-flight; real-world effect indeterminate | **never auto-retry** |

`unknown` is the finding that matters most operationally (review K3). A task
killed after `open -b com.spotify.client` was issued may well have taken
effect. Presenting that as `failed` and retrying it is how duplicate side
effects happen. Unknown outcomes are surfaced to the user for reconciliation.

## 6. Health monitoring

- Periodic `health_check()` per agent; structured results, not strings.
- Runtime-level health: queue depth, worker saturation, audit write latency,
  authorization denial rate, routing failure rate, quarantine count.
- **Denial-rate and scope-violation-rate are security signals**, not just
  metrics. A burst trips anomaly detection → kill switch.
- Health feeds the UI: the eye shows `warning` for a quarantined agent, and the
  task board shows per-agent state. Aggregate rule: any executing task →
  `executing`; any pending confirmation → `waiting`; a failure → `error` moment.

## 7. Resource management

| Resource | Control |
| --- | --- |
| Memory | bounded event history, bounded queue, bounded audit buffer, bounded session store; soak test must show flat memory |
| CPU | worker pool size; per-worker rlimits |
| Disk | audit rotation with chain continuity (review L4); retention policy; T0 sampling if volume demands |
| Network | denied by default; granted per scope token only |
| File handles | pooled; leak detection in soak tests |
| Processes | worker pool cap; orphan reaping on restart |

Long-running is the design point: NELA is expected to stay up for days. Every
structure that can grow must have a bound, and the bound must be tested by a
soak run, not assumed.

## 8. Recovery

**After a crash:**
1. Verify the audit chain; a break is alarmed, not silently repaired.
2. Reconcile `unknown`-outcome tasks with the user before anything resumes.
3. Do not restore sessions, scope tokens, or elevation — re-authenticate.
4. Roll back uncommitted pre-images if their tasks did not complete.
5. Resume the queue only after the above, and only for tasks re-authorized
   under a live session.

**After a kill switch:** recovery is explicit, audited, and never restores
revoked tokens (review K4). Offer bulk rollback of the last N actions.

**After lock:** resume requires re-authentication; elevation is not restored
(`auth_session_lock_model.md` §4).

**Degraded modes** (each explicit, each visible to the user):
- audit unavailable → T0 only
- permission engine unavailable → deny all (fail closed)
- registry unavailable → no dispatch
- secrets broker unavailable → credentialed agents unavailable, others fine
- an agent missing → honest "I can't do that yet", never a crash

## 9. Tests required

1. Soak: 24h idle + periodic tasks; memory flat, handles flat, log rotated with
   chain intact.
2. Kill switch with the Brain deliberately blocked (must still stop everything).
3. Blocking subprocess agent → timed out and actually terminated.
4. Crash mid-T2 → outcome `unknown`, no auto-retry, reconciliation prompted.
5. Queue full → rejection, not growth.
6. Two concurrent confirmation requests → serialized, no dropped intent.
7. Same-scope concurrent tasks → serialized; rollback LIFO verified.
8. Restart with checkpointed queue → tasks re-authorized, not resumed blind.
9. Boot with a tampered audit chain → degraded mode + alarm.
10. Boot with a manifest inside a writable scope → startup refused.
