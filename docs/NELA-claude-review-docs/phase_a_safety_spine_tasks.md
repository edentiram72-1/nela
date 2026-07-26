# Phase A — Safety Spine: Implementation Tasks

Implementation handoff for Codex. Translates the Phase A gate from
`docs/ai_system_roadmap.md` into numbered, dependency-ordered tasks.

**Why this phase exists:** no new agent may act until this spine is in place.
Several of these tasks are already-open review findings
(`docs/claude_review_findings.md`) — Phase A is where they finally land, in an
order where each one is buildable.

Specs: `permission_model.md` · `nela_runtime_architecture.md` ·
`multi_agent_orchestration.md`

**Global rules for every task below**
- Isolated branch per task, small commits, `docs/ai_handoff.md` updated before
  handoff, structural decisions recorded in `docs/decisions.md`.
- Brain stays agent-neutral; execution logic stays in agents.
- Full suite must pass after each task, with the **numeric** test count
  recorded (not "all tests passed").
- No user-facing Hebrew strings in code (language packs only).

---

## Dependency graph

```text
A-01 audit-log ──┬─> A-02 scope-validation ──┐
                 │                            ├─> A-05 permission-engine ─┬─> A-06 policy-before-dispatch
                 └─> A-03 capability-manifests ┤                          │
                          │                    │                          ├─> A-09 kill-switch
                          └─> A-04 capability-registry ───────────────────┘
A-07 eventbus-hardening (independent) ─────────────────────────────────────┐
A-08 idempotency-metadata ─────────────────────────────────────────────────┼─> A-10 async-execution
A-11 secrets-broker (independent, needed before any credentialed agent)    │
A-12 agent-health-lifecycle ───────────────────────────────────────────────┘
                                                                            └─> A-13 rollback-tokens
```

Recommended execution order: **A-01 → A-07 → A-02 → A-03 → A-04 → A-05 →
A-06 → A-08 → A-10 → A-09 → A-12 → A-11 → A-13.**

---

## A-01 · Append-only Audit Log

**Goal:** every action, decision, and refusal in NELA is recorded before
anything else is built on top. This is first because every later task writes
to it, and retrofitting audit is how audit gaps happen.

- **Files likely affected:** `core/audit.py` (new), `core/startup.py`,
  `core/events.py` (new event types), `config/` (log path), `docs/`
- **Dependencies:** none
- **Acceptance criteria:**
  - Append-only record: `{ts, actor, action, tier, target, decision, result, correlation_id, rollback_token}`.
  - Writes are durable and ordered; no in-process API can rewrite or delete entries.
  - Secret-pattern redaction on write (never log a token/key value).
  - `correlation_id` propagates from the conversation turn.
  - Audit write failure ⇒ system refuses state-changing actions (fail closed).
- **Tests required:** append + read-back; rewrite/delete attempt rejected; redaction of known secret shapes; fail-closed behavior when the sink errors; correlation id preserved end-to-end.
- **Security:** the log must not be modifiable by agents (T4 in the model). Redaction is mandatory, not best-effort. Consider file permissions + a tamper-evident hash chain.
- **Rollback:** additive module; disabling it must fail closed, never open.
- **DoD:** every existing dispatch path writes at least one audit record; tests green; count recorded.

---

## A-02 · Scope Validation

**Goal:** a target-checking service that answers "is this agent allowed to
touch this path / host / repo?" — the primitive the Permission Engine calls.

- **Files affected:** `core/scope.py` (new), `config/scopes.yaml` (new), tests
- **Dependencies:** A-01
- **Acceptance criteria:**
  - Filesystem scopes canonicalize (`realpath`) before comparison; `../` traversal and symlink escapes fail closed.
  - Network scopes are an explicit allowlist, **empty by default**.
  - Repo scopes distinguish protected branches (never writable).
  - Scope tokens: signed, time-boxed, single-scope, non-transferable, with expiry enforcement.
  - Unknown/unparseable target ⇒ deny.
- **Tests required:** traversal escape denied; symlink escape denied; expired token denied; token reuse by a different agent denied; empty network scope denies all hosts; protected-branch write denied.
- **Security:** this is the single highest-value test surface in Phase A — adversarial path/target cases are mandatory, not optional.
- **Rollback:** pure additive; default-deny means a bad config blocks work rather than permitting it.
- **DoD:** scope service callable, adversarial suite green, config documented.

---

## A-03 · Capability Manifests

**Goal:** each agent declares its actions and tiers statically, so an agent is
safe by construction rather than by review.

- **Files affected:** `agents/<name>/manifest.yaml` (new, per agent), `agents/base.py` (manifest attribute), `agents/registry.py`, docs
- **Dependencies:** A-01
- **Acceptance criteria:**
  - Manifest schema per `permission_model.md` §4: `agent, version, capabilities[{action, tier, scope?, sandbox?}], forbidden[]`.
  - Every existing agent (desktop, and each mock) ships one.
  - Manifest referencing an unknown action or declaring T4 ⇒ registration rejected.
  - Tiers are declared only; nothing infers a tier at runtime.
- **Tests required:** valid manifest registers; malformed/unknown-action/T4 manifest rejected; desktop manifest matches its real action list.
- **Security:** manifests are code-reviewed artifacts; an agent must not be able to rewrite its own manifest at runtime.
- **Rollback:** agents without manifests fail registration — deliberate; add manifests before merging.
- **DoD:** all registered agents have manifests; rejection paths tested.

---

## A-04 · Capability Registry

**Goal:** resolve "who can do this action on this target?" by capability, not
by string-matched agent name. Closes review finding **H1**.

- **Files affected:** `agents/registry.py`, `brain/dispatcher.py` (lookup only), `brain/planner.py` (stop hardcoding target names), docs
- **Dependencies:** A-03
- **Acceptance criteria:**
  - Registry indexes manifests → `action → [agents]`, with target/scope predicates.
  - Dispatcher resolves a task's target agent via the registry; `desktop` is the fallback for generic app launches.
  - An action not present in the resolved agent's manifest is refused before execution.
  - Fixes the live bug from the Desktop review (**D2**): `wait_until_ready` either resolves to a capable agent or is not emitted.
- **Tests required:** resolution by capability; unknown capability → clear failure (not silent); PlayMedia-via-desktop path passes end to end; manifest-absent action refused.
- **Security:** resolution never falls back to "try any agent."
- **Rollback:** keep name-based routing behind a flag for one release; remove after verification.
- **DoD:** no planner code names an agent directly for generic actions; D2 regression test green.

---

## A-05 · Permission & Approval Engine

**Goal:** the spine itself — classify, validate scope, gate by tier, record.
Closes review finding **H3**.

- **Files affected:** `core/permissions.py` (new), `core/events.py`, `config/policy.yaml`, docs
- **Dependencies:** A-01, A-02, A-03, A-04
- **Acceptance criteria:**
  - `authorize(agent, action, target, context) → Decision{allow|confirm|deny, tier, reason, scope_token}`.
  - Tier from manifest; **undetermined ⇒ T4 ⇒ deny** (deny-by-default is literal).
  - T2 gates reuse the **existing NELA-0002 confirmation flow** — no second confirmation system.
  - T3 additionally requires a live lab authorization + scope token.
  - Emits `PermissionRequested / Granted / Denied / ScopeViolation`; every branch audited.
  - Trust/relationship level has **no** effect on tier (explicit test).
  - Confirmation rate-limiting to prevent approval fatigue.
- **Tests required:** each tier's gate; unknown action → deny; scope violation → deny + event; T2 confirm→execute and deny→abort; relationship stage does not change outcome; confirmation rate limit trips.
- **Security:** the engine must be unmodifiable by agents; policy config changes are audited.
- **Rollback:** engine can be set to "deny all state-changing actions" as a safe mode; never to "allow all."
- **DoD:** engine callable and fully tested; policy defaults documented in `permission_model.md`.

---

## A-06 · Policy Enforcement Before Dispatch

**Goal:** wire the engine into the one place every action passes through, so
no code path can skip it.

- **Files affected:** `brain/dispatcher.py`, tests
- **Dependencies:** A-05
- **Acceptance criteria:**
  - `dispatch()` calls `authorize()` **before** `agent.execute()`; denial → `TaskFailed` with reason, never execution.
  - `agent.execute()` wrapped in try/except; any exception → `TaskFailed` + audit (closes Desktop review **D1**, which is currently a runtime-crash path).
  - No alternate dispatch path exists (verified by test/grep).
- **Tests required:** denied task never reaches the agent; agent raising `TimeoutExpired`/`OSError` produces `TaskFailed` not a crash; confirm-required task pauses correctly.
- **Security:** this task is what makes every other control non-optional.
- **Rollback:** revert is a single-file change, but reverting reopens D1 — treat as non-revertible without replacement.
- **DoD:** D1 regression test green; grep shows one dispatch path.

---

## A-07 · Event Bus Hardening

**Goal:** one bad subscriber must not break the Brain, and history must not
grow unbounded. Independent of the permission chain — can run in parallel.

- **Files affected:** `core/events.py`, `brain/dispatcher.py` (cancelled-task cleanup), `brain/context.py` (bounded lists)
- **Dependencies:** none
- **Acceptance criteria:**
  - Handler exceptions are isolated: remaining subscribers still receive the event; failure emits `EventHandlerFailed` and is audited.
  - `_history` bounded (deque with maxlen); `previous_commands` bounded; `cancelled_tasks` cleaned when a plan finishes.
  - `correlation_id` set on every event emitted within a turn.
- **Tests required:** raising handler doesn't block others; history caps at N; correlation id present across a full turn; cancelled-task set shrinks.
- **Security:** prevents a denial-of-service via a crashing/looping subscriber and an unbounded-memory failure mode.
- **Rollback:** additive and low risk.
- **DoD:** long-running soak test shows flat memory for history structures.

---

## A-08 · Task Idempotency Metadata

**Goal:** stop retrying actions that must not be repeated. Closes review
finding **C3**.

- **Files affected:** `brain/planner.py` (Task fields), `agents/base.py` (`AgentCommand`), `brain/dispatcher.py` (retry guard), agent manifests
- **Dependencies:** A-03 (manifests declare side-effect class)
- **Acceptance criteria:**
  - `Task` gains `idempotent: bool` and `side_effect: none|repeatable|once`.
  - Dispatcher **refuses to auto-retry** non-idempotent tasks; retries only `transient` failures on idempotent actions.
  - `command.id` documented as the idempotency key agents must dedupe on.
  - Desktop agent's `launch_application` justification recorded (macOS `open` focuses if running ⇒ idempotent).
- **Tests required:** non-idempotent failure is not retried; idempotent transient failure retried within bounds; duplicate `command.id` deduped by a test agent.
- **Security:** prevents duplicated real-world side effects (double send, double close).
- **Rollback:** defaults must be conservative — unknown ⇒ non-idempotent ⇒ no retry.
- **DoD:** C3 closed in `claude_review_findings.md`.

---

## A-09 · Kill Switch

**Goal:** one action stops everything, everywhere, immediately.

- **Files affected:** `core/runtime.py` (new), `core/permissions.py`, `brain/dispatcher.py`, `ui/` (control + locked visual)
- **Dependencies:** A-05, A-06
- **Acceptance criteria:**
  - Cancels all in-flight tasks via the existing `cancel_task` path; drains the queue.
  - Revokes all active scope tokens; drops every agent to T0.
  - Triggerable by user (UI control), by anomaly (rate-limit breach, repeated scope violations), and programmatically.
  - Eye enters a distinct locked state so the halt is unmistakable.
  - Recovery is explicit and audited — never automatic.
- **Tests required:** in-flight task cancelled; tokens invalid after trip; new dispatch denied while tripped; anomaly auto-trip; recovery requires explicit action.
- **Security:** the switch must be reachable even if the Brain is wedged — do not route it through conversation handling.
- **Rollback:** none — this is the rollback.
- **DoD:** manual and automatic trips verified; documented in the runtime doc.

---

## A-10 · Async Task Execution

**Goal:** real timeouts, interruptibility, and bounded concurrency — without
changing the synchronous `BaseAgent` contract. Closes the remaining half of
review finding **C2**.

- **Files affected:** `brain/plan_executor.py` (new — extract from `ConversationEngine`, review finding M2), `brain/dispatcher.py`, `core/runtime.py`
- **Dependencies:** A-06, A-08
- **Acceptance criteria:**
  - Agents run in a bounded worker pool owned by the executor; agent code unchanged.
  - Timeouts actually interrupt/abandon a blocked agent; task marked failed with `timed_out`.
  - Independent tasks (no `depends_on`) may run concurrently; dependent tasks respect order.
  - Plan-level `on_failure: abort|continue` replaces the per-task-mode failure logic (review **M1**).
  - Tasks sharing a filesystem scope are serialized (no write races).
  - A slow **successful** task is still reported successful, with a `TaskSlow`/`timeout_exceeded` signal — never rewritten to failure.
- **Tests required:** blocking agent is timed out without hanging the runtime; concurrency observed for independent tasks; dependency order preserved; same-scope tasks serialized; slow-success not misreported.
- **Security:** prevents a hung agent from becoming a denial of service on the whole assistant.
- **Rollback:** concurrency configurable down to 1 to fall back to today's behavior.
- **DoD:** C2 and M1/M2 closed; `ConversationEngine` no longer owns plan execution.

---

## A-11 · Secrets & Credential Broker

**Goal:** agents get scoped capabilities, never raw secrets. Required before
any credentialed agent (Git/GitHub, Browser) exists.

- **Files affected:** `core/secrets.py` (new), `core/audit.py`, `config/`, docs
- **Dependencies:** A-01, A-05
- **Acceptance criteria:**
  - Secrets stored in the OS keychain; never in repo files, memory dumps, logs, or audit entries.
  - Agents request an operation-scoped, short-lived credential; the raw secret never enters agent code.
  - Secret access is audited (agent, handle, time) without recording the value.
  - Detecting a secret in proposed committed content is a hard block (T4).
- **Tests required:** broker mints and expires scoped credentials; raw secret never returned; secret in a diff is blocked; audit contains handle not value; redaction verified.
- **Security:** the highest-consequence task in Phase A. Assume logs will be shared — nothing sensitive may reach them.
- **Rollback:** no fallback to plaintext storage under any circumstance.
- **DoD:** no credential path bypasses the broker (grep + test).

---

## A-12 · Agent Health & Lifecycle Supervision

**Goal:** a failing agent is quarantined instead of degrading the system.

- **Files affected:** `core/runtime.py`, `agents/base.py`, `agents/registry.py`, `ui/` (status surface)
- **Dependencies:** A-04, A-06
- **Acceptance criteria:**
  - Periodic `health_check()`; structured results feed the runtime and the UI.
  - States extended with `quarantined`; entry on health failure, rate-limit breach, or repeated scope violations.
  - Quarantined agents receive no tasks; recovery needs a passing health check and is audited.
  - Sleep/resume releases and reacquires resources; resume is lazy on first task.
  - Missing capability ⇒ honest "can't do that yet" from the Brain, never a crash.
- **Tests required:** unhealthy agent quarantined and not dispatched to; recovery path; repeated scope violation triggers quarantine; graceful degradation when an agent is absent.
- **Security:** quarantine is the containment mechanism for a misbehaving agent.
- **Rollback:** quarantine can be manually cleared (audited) if it misfires.
- **DoD:** lifecycle diagram in `nela_runtime_architecture.md` matches the implementation.

---

## A-13 · Rollback Tokens & Reversibility

**Goal:** every state-changing action can be undone.

- **Files affected:** `core/rollback.py` (new), `core/permissions.py`, `brain/dispatcher.py`, `core/runtime.py`
- **Dependencies:** A-05, A-06, A-09, A-12
- **Acceptance criteria:**
  - T1/T2 actions capture a pre-image before execution and store a `rollback_token` in the audit record.
  - `rollback(token)` restores the pre-image and emits `ActionRolledBack`.
  - Kill switch offers "roll back last N actions".
  - Git operations prefer reversible forms (new branch over force-push, revert over history rewrite).
  - An action whose pre-image cannot be captured is downgraded to require confirmation, or refused.
- **Tests required:** file edit rolled back byte-for-byte; rollback of an already-rolled-back token is a no-op; kill-switch bulk rollback; uncapturable pre-image path.
- **Security:** rollback must not be usable to revert *audit* entries.
- **Rollback:** meta — the rollback system itself is additive.
- **DoD:** demonstrated end-to-end on a real file edit and a git commit.

---

## Exit criteria for Phase A

- [ ] Every registered agent has a manifest and is routed by capability.
- [ ] Every action passes `authorize()` before execution; one dispatch path only.
- [ ] Audit log records every action **and every refusal**, with correlation ids.
- [ ] Kill switch verified manually and automatically.
- [ ] Non-idempotent tasks are never auto-retried.
- [ ] Blocking agent cannot hang the runtime.
- [ ] No credential path bypasses the broker; no secret appears in any log.
- [ ] Review findings closed: **C2, C3, H1, H3, D1, D2, M1, M2**.
- [ ] Test count recorded in `docs/ai_handoff.md` after each task.

Only after all boxes are checked does NELA 1.0 agent work (Coding, Git,
passive Cyber, Research) begin.
