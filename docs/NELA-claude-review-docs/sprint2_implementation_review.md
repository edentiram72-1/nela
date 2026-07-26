# Sprint 2 — Implementation Review (Actual Code)

Reviewed: `nela-sprint2-claude-review.zip`, branch
`feature/NELA-safety-spine-routing`, commit `860fbd9`.
Method: read every implementation file, ran the tests that were runnable.

**Evidence honesty:** the bundle is a slice, not a runnable repo — `agents/base.py`
and some deps are absent, so 27 of 59 tests collected and passed; the 4 errors
are `ModuleNotFoundError`, not logic failures. Verdicts below are grounded in
the code that *is* present; where a claim can't be verified from the slice it is
marked NOT REVIEWABLE, not passed.

This is genuinely strong work. Every finding was engaged seriously; most are
real passes. The gaps that remain are specific and small.

---

## 1. Findings table

| ID | Finding | Verdict |
| --- | --- | --- |
| A1 | WebView bridge authentication | **PASS** |
| K1 | Subprocess isolation & kill switch | **PARTIAL** |
| P1 | TOCTOU protection | **PARTIAL** |
| P2 | Confirmation binding | **PASS** |
| R1 | Agent Registry overwrite protection | **PARTIAL** |
| L1 | Audit hash-chain integrity | **PARTIAL** |
| T1 | Authorization-safe routing | **PASS** |
| T2 | Prompt-injection-resistant routing | **PASS** |

Plus, from my earlier NELA-0002 review: `CloseApplication` and `StopTask` now
carry `requires_confirmation=True` — the inverted-safety finding is **fixed**,
and `_resolve_confirmed` re-plans from the stored original `intent` rather than
the reply text — the "memory stores 'yes'" finding is **fixed**. Good.

---

## 2. PASS findings (evidence)

**A1 — PASS.** `ui/secure_bridge.py::SecureLocalBridge`. Unix domain socket,
`path.chmod(0o600)`, `socket.AF_UNIX`; token from `secrets.token_urlsafe(32)`;
verification via `hmac.compare_digest`; `Origin` checked against
`expected_origin`; `null`/missing origin rejected. Tests assert socket family,
`0600`, and all three reject paths. No `0.0.0.0`, no `==` token compare. Meets
every [CRIT] criterion in the verification doc.
*Note (not blocking):* this is the transport primitive; when it is wired to a
real request handler, re-verify that no route mutates state on GET and that the
token is injected into the webview without landing in argv or a file.

**P2 — PASS.** `permissions/confirmation.py::action_tuple_hash` +
`engine._confirmation_error`. Confirmation is bound to a SHA-256 over the
canonicalized `(agent, capability, action, target, parameters, session,
expires_at)` tuple; mismatch → `CONFIRMATION_MISMATCH` (distinct decision, a
security signal); expiry parsed and enforced; parameter noise stripped via
`IGNORED_PARAMETER_KEYS`. Swapping any bound field invalidates the hash. Meets
[CRIT] 1–5. (Single-use consumption and the one-pending-slot invariant belong
to X1 — see §4.)

**T1 — PASS.** `permissions/engine.py::authorize`. Tier is derived from the
capability manifest of the concrete agent (`tier = capability.tier if
capability else T4`) and every gate (kill switch, lock, scope, confirmation)
runs *after* the candidate is chosen. `brain/dispatcher.py::_authorize_task_route`
resolves candidates from the registry, then calls `authorize()` per candidate
and only dispatches on `permission.granted`. Undetermined capability ⇒ T4 ⇒
deny (deny-by-default is literal). Routing cannot grant a tier — the two-gate
structure holds.

**T2 — PASS.** `find_agents_for_capability` selects purely from
`capability_id` + `platform` against declared manifests. No file content, web
text, or `raw_text` reaches routing — `intent_router.classify` maps keywords to
a structured `Intent`, and routing consumes `task.capability`, not prose. A
repo README cannot steer selection. Candidate resolution is deterministic
(`sorted(agents)`).

---

## 3. PARTIAL findings (severity · file · symbol · scenario · fix · test)

### K1 — PARTIAL · HIGH
- **File / symbol:** `agents/process_isolation.py::IsolatedAgentProcessRunner`;
  `permissions/engine.py::activate_kill_switch`.
- **What passes:** subprocess isolation is real — `multiprocessing.Process`,
  `join(timeout)`, `terminate()` then `kill()`, `TIMED_OUT`/`UNKNOWN` outcomes
  including the empty-queue `unknown`. This is the correct mechanism.
- **Gap 1 (HIGH):** the runner exists but is **not wired into the dispatcher**.
  `dispatcher.dispatch` still calls `agent.execute(command)` synchronously in
  the main process. So today a blocking agent still hangs the runtime — the
  capability is built but not connected. `activate_kill_switch` flips a flag and
  revokes sessions but **cannot terminate an in-flight `agent.execute`** because
  that call isn't running in the isolated runner.
- **Gap 2 (MEDIUM):** kill-switch reachability. `activate_kill_switch` is a
  method on the engine; there is no evidence of an out-of-band trigger path
  independent of the Brain/event loop. If the dispatch thread is wedged, nothing
  reachable trips it.
- **Failure scenario:** an agent action blocks on I/O; timeout can't interrupt
  it (not in a subprocess); user hits kill switch; the flag sets but the wedged
  call continues to completion, possibly taking effect.
- **Minimum fix:** route blocking/T2/T3 `agent.execute` calls through
  `IsolatedAgentProcessRunner` in the dispatcher; have `activate_kill_switch`
  signal the runner to terminate live workers; expose a trigger that does not
  traverse the Brain.
- **Required test:** dispatcher runs an agent that sleeps past its timeout →
  worker actually terminated, runtime still responsive; kill switch tripped with
  the dispatch path deliberately blocked → in-flight work stops.

### P1 — PARTIAL · HIGH
- **File / symbol:** `permissions/scope.py` (`_canonicalize_path`,
  `_file_identity`, `ScopeValidationResult.st_dev/st_ino`).
- **What passes:** canonicalization resolves symlinks and rejects `..` escapes
  via `relative_to`; protected paths (`~/.ssh`, Keychains) denied; the result
  *captures* `st_dev`/`st_ino` — the raw material for TOCTOU-safe execution is
  present.
- **Gap (HIGH):** the captured identity is **never enforced at execution**.
  `ScopeValidationResult` returns `st_dev/st_ino`, but nothing threads them to
  the agent, and the dispatcher passes `task.payload` (containing the original
  path string) to `agent.execute`. The agent re-opens the path by name. So the
  check-time identity and the execute-time object can differ — the classic
  TOCTOU window is open. The capture is decorative until consumed.
- **Failure scenario:** authorize resolves `/proj/x` (a real file); between
  authorize and the agent's `open('/proj/x')`, `x` is swapped for a symlink to
  `~/.ssh/id_rsa`; the agent acts on the wrong object.
- **Minimum fix:** carry the validated identity (or an open fd) into execution;
  the agent acts on the fd, or re-stats and compares `st_dev/st_ino` immediately
  before the syscall and aborts on mismatch. No desktop path exercises this yet
  (desktop targets are app bundle ids, not file paths), so it is not yet live —
  but it must land before any file-writing agent (coding.files.write) is
  enabled.
- **Required test:** swap target for a symlink between authorize and execute ⇒
  denial; different-file swap ⇒ denial.

### R1 — PARTIAL · MEDIUM
- **File / symbol:** `agents/registry.py::AgentRegistry`.
- **What passes:** `register()` is now insert-only — duplicate name appends
  `rejected_duplicate` to the audit list and raises `DuplicateAgentError`. The
  exact defect I flagged (`self._agents[name] = agent` silent overwrite) is
  fixed for the primary path.
- **Gap 1 (MEDIUM):** `replace()` and `_store()` still call
  `self._agents.update({agent.name: agent})` with no guard — a public
  `replace()` bypasses the insert-only protection. If any caller uses
  `replace()` on an unknown name, it becomes a silent insert; on a known name,
  a silent overwrite. The protection is one method-call away from being void.
- **Gap 2 (LOW):** the two registries (`agents/registry.py` and
  `permissions/registry.py`) both track agents with divergent overwrite rules.
  `CapabilityRegistry.register_manifest` has its own duplicate guard (good), but
  `register_agent` silently `replace=True`s when an agent re-registers over a
  baseline — a path worth an explicit test.
- **Failure scenario:** future orchestration code calls `replace()` to "update"
  an agent; a name typo silently inserts a shadow agent that then wins capability
  routing.
- **Minimum fix:** `replace()` should require the name to already exist (raise
  otherwise), and `_store` should be the only writer with an explicit
  `expect_exists: bool`. Add conformance: an agent whose manifest tier/scope
  doesn't match its behavior should fail registration (R3 from the criteria doc
  — not present).
- **Required test:** `replace()` on an unknown name raises; duplicate capability
  claim across two agents resolves deterministically or errors at registration.

### L1 — PARTIAL · HIGH
- **File / symbol:** `permissions/audit.py::AuditLog`, `entry_hash`,
  `verify_chain`.
- **What passes:** genuine hash chain — each record carries `previous_hash`,
  `entry_hash = sha256(record without entry_hash)`; `verify_chain()` walks and
  validates links; redaction of sensitive keys and secret patterns; structured
  JSON serialization (no string concatenation); `to_dict` is length-agnostic but
  fields are typed. Engine fail-closes T2/T3 on `AuditWriteError`. This is well
  above a naive append log.
- **Gap 1 (CRITICAL for durability, but Sprint-2-acceptable):** the default
  `AuditLog()` has **`sink=None`** — records live in a Python list and the
  `fsync` path is dead code unless a sink is injected. The engine constructs
  `AuditLog()` with no sink. So in the running system today the audit log is
  **in-memory only**: it does not survive a crash, and "fail-closed on write
  failure" never triggers because there is no write. The hash chain protects
  against in-process tampering but not against process death or an attacker with
  memory access. The docstring is honest that this is intentional for Sprint 2 —
  I accept it *as a sprint state*, but it must be flagged loudly: **the tamper-
  evidence guarantee is not yet real at rest.**
- **Gap 2 (MEDIUM):** `SECRET_PATTERNS` is a denylist (`ghp`, `sk-`, PEM). Novel
  secret shapes pass through. Acceptable as second-line defence *if* values
  never enter the log — but `result_message` and `target` are redacted only by
  pattern, and an agent error string could carry a secret in an unmatched shape.
- **Failure scenario:** crash after a T2 action → the record that proves it
  happened is gone (in-memory only); or a novel-format secret in an error
  message reaches the log.
- **Minimum fix (before 1.0, not before merge):** inject a real file sink so the
  `fsync` path is live and T2/T3 truly fail-closed; verify the chain at startup
  and degrade to T0 on a break; carry chain heads across rotation.
- **Required test:** with a file sink, tamper a record on disk → `verify_chain`
  fails at load; T2 with a failing sink → action denied.

---

## 4. Other subsystems reviewed

- **Permission Engine** — strong. Correct gate order (auth → capability → T4 →
  disabled → kill → lock → scope → confirmation → grant), deny-by-default,
  `enabled=False` capabilities refused (coding.files.write / git.commit /
  terminal.execute are declared-but-disabled foundations — good, they can't run
  yet). 12 tests.
- **Scoped sessions** — `ScopedSession` with expiry, agent/tier allowlists, T3
  gated on a live session owned by the same user. **Gap (MEDIUM):** expiry is
  wall-clock (`datetime.now`), not monotonic — a clock change can extend a
  session (criteria A3). Fix before 2.0 when T3/lab lands.
- **Agent manifests** — declarative, `MINIMUM_CAPABILITY_TIERS` floor enforced
  at registration (a manifest can't claim *lower* than the floor). Sound. Note:
  no conformance tests proving code matches manifest (R3) — track.
- **Lock mode** — `set_lock_mode` + engine gate (locked ⇒ only T0). Correct at
  the permission layer. **Not reviewable here:** the criteria require that voice
  wake cannot bypass lock (A2) and the eye shows a distinct locked state — those
  live in voice/UI, not in this bundle. NOT REVIEWABLE.
- **Kill switch** — permission-layer behavior correct (flag + session revocation
  + T0-only). Execution-layer termination is the K1 gap above.
- **Event Bus hardening** — `core/events.py`: `deque(maxlen=...)`, per-subscriber
  try/except with `event_subscriber_failed` logging, `correlation_id` on events.
  Matches the hardening spec. **PASS.**
- **Capability routing** — deterministic, capability-based, platform-filtered,
  first-authorized-candidate wins with first-denial fallback. Closes H1. Good.
- **Hebrew clarification flow** — `_classify_confirmation_answer` handles Hebrew
  affirmatives/negatives (כן/מאשר/תמשיך, לא/בטל/עצור), TTL expiry, unclear-reply
  cap, pending-slot follow-up, and re-plans from the stored intent. Two carried
  gaps: (a) **still exact-set matching** — "כן בבקשה" / "yes please" classify as
  unclear (my prior HIGH finding, MEDIUM now that max_unclear buffers it);
  (b) **"אל" and "stop" in negatives** — "אל" is a common Hebrew preposition and
  "stop" collides with StopTask; safe under exact match, becomes a bug the day
  matching goes token-based. Track both.
- **X1 (concurrent confirmations)** — `oldest_pending_confirmation()` handles
  one, but nothing enforces a single slot, and confirmations aren't marked
  single-use/consumed. With async execution (K1 wiring) this becomes reachable.
  MEDIUM, fix alongside K1.

---

## 5. Required fixes

**Before merge (HIGH):**
1. **K1** — wire `IsolatedAgentProcessRunner` into the dispatcher for
   blocking/T2/T3 execution, and make the kill switch terminate live workers.
   The mechanism exists; it isn't connected, so the runtime-hang risk is still
   live.
2. **R1** — close the `replace()`/`_store()` overwrite bypass; make `replace()`
   require an existing name.

**Before 1.0 (HIGH, not blocking this merge given nothing exercises them yet):**
3. **P1** — enforce the captured `st_dev/st_ino` (or an fd) at execution. Must
   land before `coding.files.write` is enabled.
4. **L1** — inject a durable file sink so `fsync`/fail-closed are live and the
   chain survives a crash; verify chain at startup.

**Track (MEDIUM/LOW):**
5. Scoped-session expiry → monotonic clock (before T3/lab).
6. Confirmation classifier → token-based, negative-takes-precedence; remove
   "אל" as a standalone negative.
7. Single-use confirmations + single pending slot (with K1).
8. Manifest conformance tests (R3).

---

## 6. Missing evidence (NOT REVIEWABLE)

- Voice-wake-cannot-bypass-lock (A2) and the locked-eye visual — not in bundle
  (voice/UI).
- `agents/base.py` and full dep tree — so end-to-end dispatch-through-permission
  and the full 59-test run could not be executed here; 27 collected passed.
- Startup chain-verification and log rotation — not present (consistent with the
  in-memory Sprint-2 audit state).

---

## 7. Merge decision

# APPROVE WITH REQUIRED FIXES

The architecture is implemented faithfully and the security-critical structure —
deny-by-default, two-gate routing, confirmation binding, bridge auth, engine
gate order — is correct and evidenced. Four of eight findings are clean passes;
the two carried NELA-0002 findings are fixed.

The two **before-merge** fixes (K1 wiring, R1 `replace()` bypass) are required
because each is a case where a safety mechanism is *built but circumventable*:
K1's isolation exists but isn't in the execution path, and R1's insert-only
guard has a public bypass. Neither is a redesign — both are small, local
changes to code already written. P1 and L1 are real but not yet reachable
(no file-writing agent is enabled, audit is intentionally in-memory this
sprint); they are hard gates for 1.0, not this merge.

Fix K1 and R1, add their two tests, and this is an APPROVE.
