# NELA Runtime & Lifecycle Architecture

How NELA grows from a single-Brain desktop assistant into a supervised
multi-agent system, without changing the Brain's agent-neutral contract.

Status: specification only. The current Brain, Dispatcher, EventBus, Memory,
UI, Voice, Language, and Desktop Agent are treated as fixed foundations.

---

## 1. The shape of the system

```text
                    ┌──────────────────────────┐
                    │        NELA Runtime       │  lifecycle, health, kill switch
                    └────────────┬─────────────┘
                                 │ owns
      ┌──────────────┬───────────┼───────────┬──────────────┐
      ▼              ▼           ▼           ▼              ▼
   Brain        EventBus   Permission     Task Queue     Audit Log
 (unchanged)   (unchanged)  Engine     + Orchestrator   (append-only)
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │      Agent Registry       │
                    └────────────┬─────────────┘
     ┌──────────┬──────────┬─────┴────┬──────────┬──────────┐
     ▼          ▼          ▼          ▼          ▼          ▼
  Desktop    Coding     Review/QA   Git/GitHub  Cyber    Research
 (exists)                                      (lab-only)
                                                            ▼
                                              Browser · Vision · PM
```

The Runtime is the only new top-level authority. Everything under it either
already exists or is an agent behind the existing `BaseAgent` contract.

## 2. NELA Runtime

**Purpose:** own process lifecycle, agent health, resource governance, and the
kill switch. It is the supervisor; it does no domain work.

**Responsibilities:**
- Bootstrap (extends `core/startup.py`): construct Brain, EventBus, Permission
  Engine, Task Queue, Audit Log, Memory, then register agents from manifests.
- Health: periodic `health_check()` on every agent; quarantine an agent that
  fails or breaches rate limits (drop to T0, stop routing to it).
- Kill switch (`permission_model.md` §5): global stop + token revocation.
- Graceful degradation: if an agent is unavailable, the Brain still answers;
  missing capability ⇒ honest "I can't do that yet," never a crash.

**Failure modes:** an agent hangs (→ per-task timeout + quarantine), the
permission engine is unreachable (→ fail closed, everything becomes T4), the
audit log can't write (→ halt state-changing actions, T0-only until restored).

## 3. Agent lifecycle

Extends the existing `AgentState` (`created/ready/running/stopped/error`) with
supervised transitions:

```text
 register → validate manifest → ready ⇄ running
     │                           │        │
     │                       quarantine ← fail/breach
     ▼                           │
   rejected (bad manifest)    recovered → ready
```

- **register:** manifest loaded, capabilities indexed by the Permission Engine.
  A manifest referencing an unknown action or T4 capability is rejected.
- **sleep/resume:** idle agents release resources; resume is lazy on first
  task (already partially in the dispatcher's `initialize()` call).
- **quarantine:** health failure or rate-limit/scope breach. No tasks routed;
  audited; user-visible. Recovery requires a passing health check.
- **report health:** structured `health_check()` feeds the Runtime's monitor
  and the eye (a quarantined agent can surface as a `warning` moment).

## 4. Task queue & orchestration

Full spec in `multi_agent_orchestration.md`. In brief: the Runtime owns a
priority queue of tasks; the Orchestrator assigns tasks to agents by
capability, respects `depends_on`, runs independent tasks concurrently in a
worker pool (this is where the async execution model from the Phase 1 review
finally lands), and enforces that every dispatch passes the Permission Engine.

## 5. The 15 systems, mapped

| # | System | Where it lives | Doc |
| --- | --- | --- | --- |
| 1 | Runtime & lifecycle | this doc | — |
| 2 | Permission & approval | Permission Engine | `permission_model.md` |
| 3 | Coding Agent | agent + manifest | `coding_agent_spec.md` |
| 4 | Code Review Agent | agent | `coding_agent_spec.md` §7 |
| 5 | Test/QA Agent | agent | `coding_agent_spec.md` §6 |
| 6 | Git/GitHub Agent | agent | `coding_agent_spec.md` §5 |
| 7 | Defensive Cyber Agent | agent (lab-bound) | `cyber_agent_spec.md` |
| 8 | Isolated Cyber Lab | sandbox host | `cyber_agent_spec.md` §4 |
| 9 | Research Agent | agent | this doc §6 |
| 10 | Browser & Vision Agents | agents | this doc §6 |
| 11 | Project Manager Agent | meta-agent | `multi_agent_orchestration.md` §5 |
| 12 | Task queue & orchestration | Orchestrator | `multi_agent_orchestration.md` |
| 13 | Persistent memory & project knowledge | Memory subsystem | this doc §7 |
| 14 | Audit logging & rollback | Audit Log | `permission_model.md` §5 |
| 15 | Secrets & credentials | Keychain broker | `permission_model.md` §5 |

## 6. Research, Browser, Vision agents (specs in brief)

- **Research Agent (T0-heavy):** plans a query, fetches via the Browser Agent,
  extracts and cross-references, writes a sourced summary to project memory.
  All reads (T0); writing findings to a file is T1. Never executes code it
  finds. Copyright-aware: stores links + paraphrase, not scraped article text.
- **Browser Agent:** navigation, form fill, extraction — T0 for reads, T2 for
  any submit/purchase/auth action. Network scope applies. No credential entry
  without a minted, scoped capability.
- **Vision Agent (exists as interface):** screen reading, OCR, UI element
  detection to help other agents locate targets. T0 (pure observation); it
  never acts, only informs.

## 7. Persistent memory & project knowledge

Built on the delivered Memory subsystem:
- **Project memory** (`memory` long-term + semantic): architecture facts,
  decisions, conventions per repo — so the Coding Agent understands a codebase
  across sessions instead of re-reading cold every time.
- **Episodic** records agent actions and milestones (finished features,
  merged PRs, security findings) for "what did we do on X?".
- **Scope grants, ownership proofs, audit summaries** are project-scoped and
  survive restarts (needs the Phase-4 persistence backend; until then, in
  memory with the durability warning).
- Trust arc affects *tone* (Language) only — never *permission tier*.

## 8. What must not change

- The Brain stays agent-neutral; orchestration lives in the Runtime, not the
  Brain.
- The `BaseAgent` contract is extended by manifests, not rewritten.
- The EventBus remains the one communication channel; new events are additive.
- No agent talks to another agent directly — they coordinate through the
  Orchestrator, the Task Queue, files, and GitHub (DEC-0001 holds at the agent
  layer too).
