# Claude Review Findings

This document captures Claude's architecture review findings for the Phase 1 Brain foundation.

Claude does not connect directly to NELA OS. These findings were produced from the generated review bundle and are stored here so Codex, ChatGPT, Claude, and future assistants can continue from the same GitHub source of truth.

## Review Target

- Repository: `https://github.com/edentiram72-1/nela`
- Branch: `feature/NELA-0001-foundation-architecture`
- Scope: Phase 1 Brain foundation
- Review areas: confirmation flow, dispatcher safety, idempotency, event bus robustness, intent matching, permission policy, capability registry, and long-term maintainability.

## Critical Findings

### C1: Confirmation Deadlock

Pending confirmations are not resolved before new intent classification.

Impact:

- After the Brain asks a clarifying or confirmation question, a follow-up answer is treated as a new message instead of resolving the pending confirmation.
- The conversation remains stuck in `WAIT` deterministically because `resolve_confirmation()` is never called.
- Real users may be unable to approve, reject, or clarify sensitive tasks.

Recommended fix:

- Check pending confirmations before classifying a follow-up message as a new intent.
- Resolve approval and rejection replies explicitly.
- Support unclear replies by asking again or cancelling after a defined limit.
- Add expiry or cancellation semantics.
- Add tests for approval, rejection, unclear reply, and repeated follow-up behavior.

Tracking task:

- `NELA-0002-confirmation-deadlock`

### C2: Timeout Is Checked After Execution

Dispatcher timeout metadata is evaluated after synchronous execution.

Impact:

- A slow task can complete successfully and then be rewritten as failed.
- Retry logic may duplicate side effects after the action already happened.
- `started_at` being outside retry handling can make timing inaccurate.

Recommended fix:

- Track timeout per attempt.
- Do not rewrite a completed successful task as failed after the fact.
- Treat current timeout values as advisory until task execution can be moved to async workers or cancellable execution.

Tracking task:

- `NELA-0003-dispatcher-timeout-retry-safety`

### C3: Retries Lack Idempotency Rules

The dispatcher can retry tasks without knowing whether a task is safe to repeat.

Impact:

- Non-idempotent actions, such as sending messages, creating files, changing settings, or executing shell commands, could run more than once.
- Future real Agents would inherit unsafe retry behavior.

Recommended fix:

- Add idempotency metadata to `Task` and `AgentCommand`.
- Mark tasks as idempotent, non-idempotent, or unknown.
- Refuse automatic retries for non-idempotent or unknown side-effecting tasks.
- Use command IDs as idempotency keys where Agents support them.

Tracking task:

- `NELA-0004-task-idempotency`

## High Priority Findings

### H1: Intent Matching Is Too Broad

Rule-based substring matching can misclassify messages.

Example risk:

- Words containing action-like substrings can trigger the wrong intent.
- Agent routing by string coincidence can select the wrong capability.

Recommended fix:

- Move toward explicit patterns, normalized tokens, and confidence scoring.
- Keep deterministic matching for tests, but make unsupported or ambiguous intent states explicit.

Tracking task:

- `NELA-0005-intent-matching-hardening`

### H2: Permission Policy Is Missing Or Incomplete

The Brain has early confirmation concepts, but no central permission model for real-world actions.

Impact:

- Real terminal, desktop, browser, file, and communication Agents need consistent approval rules.
- Stop/cancel semantics and sensitive action semantics can become inconsistent across Agents.

Recommended fix:

- Add a `PermissionPolicy` layer before real external Agents execute.
- Define sensitivity classes for destructive, external, financial, personal data, system setting, and communication actions.
- Require confirmation before unsafe or irreversible work.

Tracking task:

- `NELA-0006-permission-policy`

### H3: Event Bus Needs Isolation And Bounded History

The in-process Event Bus should isolate subscriber failures and avoid unbounded growth.

Impact:

- One failing subscriber can affect unrelated event consumers.
- Unbounded event history can become a memory issue in long sessions.

Recommended fix:

- Catch and log subscriber exceptions per handler.
- Add bounded event history or configurable retention.
- Consider event correlation IDs and trace IDs as the system grows.

Tracking task:

- `NELA-0007-event-bus-hardening`

### H4: Capability Registry Needs Clearer Boundaries

Agent availability and capability discovery need to become explicit before real plugins and Agents are introduced.

Impact:

- Planner and Dispatcher may not know which Agent can safely handle a task.
- Runtime registration can become fragile when plugins are added.

Recommended fix:

- Add capability descriptors to registered Agents.
- Support health and availability checks.
- Keep developer-only review Agents separate from runtime user-facing Agents.

Tracking task:

- `NELA-0008-capability-registry`

## Medium Priority Findings

### M1: `TaskMode` Semantics Are Conflated

Sequential, parallel, conditional, retry, timeout, and cancellation logic should become execution concerns rather than only plan metadata.

Recommended fix:

- Introduce a `PlanExecutor` later to own execution semantics.
- Keep Planner focused on decomposition and task metadata.

Tracking task:

- `NELA-0009-plan-executor`

### M2: Correlation IDs Are Underused

Correlation IDs exist conceptually but are not yet consistently used across events, tasks, dispatcher results, and logs.

Recommended fix:

- Propagate `correlation_id` through Conversation, Intent, Plan, Task, AgentCommand, AgentResult, and Events.
- Use IDs for logs, debugging, replay, and audit trails.

### M3: Memory Paths Need One Clear Write Flow

Remembering user preferences and long-term facts should use one explicit path.

Additional observed issue:

- `Remember` requests create a Plan with a task targeting a future `memory` Agent that is not registered, while durable memory writes also happen through `MemoryManager`. This creates misleading telemetry and should be cleaned up in a follow-up.

Recommended fix:

- Route durable memory updates through `MemoryManager`.
- Emit `MemoryUpdated` events from one central place.
- Add tests for remember/update/retrieve behavior.

### M4: README Diagram Needs Current Brain Components

The README architecture diagram should explicitly show the Decision Engine and Dispatcher so it matches the current Brain implementation.

## Recommended Execution Order

1. `NELA-0002-confirmation-deadlock`
2. `NELA-0003-dispatcher-timeout-retry-safety`
3. `NELA-0004-task-idempotency`
4. `NELA-0007-event-bus-hardening`
5. `NELA-0005-intent-matching-hardening`
6. `NELA-0006-permission-policy`
7. `NELA-0008-capability-registry`
8. `NELA-0009-plan-executor`
9. First real external Agent

## Next Step

Codex should start with `NELA-0002-confirmation-deadlock`.

Do not implement real external Agents until confirmation handling, dispatcher retry safety, and permission policy have been hardened enough to prevent unsafe repeated or unapproved actions.
