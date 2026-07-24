# Multi-Agent Orchestration

How many agents cooperate on one goal without chaos, without talking to each
other directly, and without ever bypassing the Permission Engine.

Status: specification only. Builds on the existing Planner, Dispatcher, and
EventBus; extends them, replaces nothing.

---

## 1. Principles

1. **The Orchestrator assigns; agents execute.** Agents never pick their own
   work or call each other. They receive tasks and return results.
2. **Files & GitHub are the shared state** (DEC-0001, extended to agents). Two
   agents coordinate by reading/writing repo files, PRs, and the task queue —
   not by a direct channel.
3. **Every dispatch passes Permission** (`permission_model.md`). Orchestration
   never has a fast path around the tier gate.
4. **The Brain stays agent-neutral.** Orchestration is a Runtime concern; the
   Brain produces plans, the Orchestrator runs them.

## 2. Task model

Extends the existing `Task`/`Plan` with the fields the Phase 1 review already
recommended (idempotency, real dependencies):

```yaml
task:
  id: uuid
  goal: "add rate limiting to the login endpoint"
  agent: coding            # resolved by capability, may be unset → orchestrator picks
  action: edit_file
  tier: T1                 # from the agent manifest
  depends_on: [t_read, t_test_written]
  idempotent: false        # closes review finding C3
  side_effect: once|repeatable|none
  scope: [filesystem.project]
  priority: normal
  retry: {max: 1, on: [transient]}   # never auto-retry non-idempotent
  correlation_id: <turn/plan id>
```

## 3. The queue

- **Priority queue** owned by the Runtime: `urgent > high > normal > low`,
  FIFO within a level.
- **Dependency-aware:** a task is eligible only when all `depends_on` are
  `completed`. This replaces the fragile per-task-mode failure logic flagged in
  the review (M1) with explicit dependencies + a plan-level `on_failure:
  abort|continue`.
- **Concurrency:** independent eligible tasks run in a bounded worker pool.
  This is where the async execution model the Phase 1 review asked for lives —
  the Agent contract stays synchronous; the Orchestrator runs agents in
  workers, giving real timeouts and interruptibility without touching agent
  code.

## 4. Scheduling & failure

```text
loop:
  pick highest-priority eligible task
  authorize(agent, action, target)   ── deny → TaskFailed, maybe re-plan
  snapshot (rollback token)
  run in worker (timeout, sandbox per tier)
  on success → mark completed, unblock dependents
  on failure:
     idempotent + transient → retry (bounded)
     else → TaskFailed; apply plan on_failure policy
  emit events throughout; audit every step
```

Kill switch drains the queue and cancels in-flight workers via the existing
`cancel_task` path.

## 5. Project Manager Agent

A meta-agent that turns a goal into a plan of tasks across other agents. It is
the only agent that *creates* tasks — and it still can't execute domain
actions itself.

**Responsibilities:**
- Decompose a feature ("add OAuth login") into ordered tasks: research →
  code → tests → review → PR, with dependencies.
- Assign by capability (reads agent manifests), never by name.
- Sequence and gate: hold a PR task until Review + QA tasks pass.
- Track project state in project memory (episodes for milestones, semantic
  facts for decisions).
- Surface status to the user: what's done, blocked, waiting on confirmation.
- Escalate: anything risky or ambiguous goes to the human, not resolved
  autonomously.

**The PM cannot:** execute code, push, scan, or approve its own tasks' risky
tiers. It plans; the Permission Engine and humans gate.

## 6. Coordination protocol (no direct agent-to-agent)

```text
PM writes tasks → Queue
Coding Agent completes → writes branch + PR, result to Queue
Review Agent picks review task (depends_on: PR exists) → annotates PR
QA Agent picks test task → posts results to PR
PM sees all three green → surfaces "ready to merge" to human
Human (or policy) merges
```

Every arrow is a file/PR/queue write plus an event — inspectable, auditable,
replayable. If any agent vanishes mid-flight, its task times out and requeues;
no other agent is blocked waiting on a direct call.

## 7. Conflict handling

- **Two agents, same files:** the Orchestrator serializes tasks that share a
  filesystem scope (a simple per-scope lock); it never lets two writers race.
- **Divergent branches:** the Git Agent rebases; unresolved → human.
- **Contended confirmations:** the single-confirmation-slot rule from the
  NELA-0002 review is enforced queue-wide — at most one pending confirmation;
  others wait.

## 8. Observability

- Every task transition emits an event; the Runtime exposes a live task board
  (feeds the UI). The eye reflects aggregate state: any `executing` task →
  `executing`; a pending confirmation → `waiting`; a failure → `error` moment.
- `correlation_id` threads a whole feature — from the user's sentence through
  every agent action to the merged PR — for audit and debugging.

## 9. Roadmap fit

- **1.0:** single-agent tasks, sequential, human-confirmed. Queue exists but
  concurrency = 1.
- **2.0:** PM decomposes features; Review/QA gate; bounded concurrency for
  independent tasks.
- **3.0:** supervised multi-agent features end-to-end on allowlisted repos;
  human holds merge + kill switch.
