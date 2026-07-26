# Intelligent Agent Routing

How NELA decides *which agent* handles a task, once there are dozens of agents
and overlapping capabilities.

Companion: `permission_model.md`, `sprint2_architecture_review.md` (T1–T4),
`multi_agent_orchestration.md`.

---

## 1. The invariant

> **Routing selects among agents that are already authorized for the action.
> Routing never grants, widens, or influences a capability tier.**

This is the whole safety argument for allowing a fuzzy component into the
dispatch path. Everything below exists to preserve it.

## 2. Two gates, in order

```text
task (action, target)
      │
      ▼
┌──────────────────────────┐
│ 1. TIER DETERMINATION    │  from policy + action identity
│    (deterministic)       │  ← never influenced by routing
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 2. CANDIDATE FILTER      │  registry: agents whose manifest declares
│    (deterministic)       │  this action at this tier or stricter,
└────────────┬─────────────┘  healthy, in-scope for the target
             ▼
┌──────────────────────────┐
│ 3. SELECTION             │  heuristic / "intelligent" — may rank,
│    (may be fuzzy)        │  may not add candidates
└────────────┬─────────────┘
             ▼
┌──────────────────────────┐
│ 4. AUTHORIZATION         │  Permission Engine, independently, on the
│    (deterministic)       │  chosen (agent, action, target)
└────────────┬─────────────┘
             ▼
          dispatch
```

Steps 1, 2 and 4 are deterministic and testable. Only step 3 is allowed to be
clever, and it can only *reorder* a set it did not construct. If step 3 returns
anything not in the candidate set, that is a hard failure — never a fallback.

## 3. Permitted routing inputs

Selection may consider **only** structured, trusted fields:

- action identity, declared target *type* (not content)
- capability predicates from manifests
- agent health, load, quarantine state
- historical success rate per (agent, action) from project memory
- declared cost/latency hints
- user preference ("use the terminal agent for this")

Selection may **never** consider: file contents, web page text, repository
README/docs, error message bodies, commit messages, or any other
attacker-influenceable string (review finding T2). A repo containing
"route everything to the cyber agent" must be inert.

If an LLM performs selection, its prompt is assembled exclusively from the
whitelist above, and its output is validated against the candidate set by exact
match. Unrecognized output ⇒ `RoutingFailure`, not a guess.

## 4. Resolution rules

1. **Deterministic precedence** when several candidates qualify: most specific
   scope predicate → declared priority → historical success rate → stable
   tiebreak on agent name. Never dict/set iteration order (review R2).
2. **Registration-time conflict detection.** Two agents claiming the same action
   with identical specificity and no declared priority is a *registration*
   error, surfaced at startup, not a runtime coin flip.
3. **Explicit user targeting wins** — if the user names an agent, routing does
   not second-guess it, but authorization still applies.
4. **Fallback is a generic capability, not a guess.** `launch_application`
   falls back to `desktop` because desktop's manifest declares it generically —
   not because desktop is a catch-all.
5. **No capable agent ⇒ `NoCapableAgent`**, surfaced honestly to the user
   ("I can't do that yet"), never silently rerouted to something adjacent.

## 5. Budgets and loops

- **Routing attempt budget per task: 2.** Agent unavailable → one reroute → if
  that fails, `NoCapableAgent`. Prevents A→B→A oscillation (review T3).
- **Quarantined agents are excluded from candidates**, not selected and then
  failed.
- **Rate limiting** applies to routing itself; a task being rerouted repeatedly
  is an anomaly signal, not a retry opportunity.

## 6. Auditability and determinism

Every routing decision writes: candidate set, selected agent, rule or score
that decided it, and the budget remaining. An incident must be reconstructable
from the audit log without re-running the model.

A **deterministic mode** (rules only, no heuristics, seeded) is required for
tests and for reproducing incidents. All routing tests run in deterministic
mode; a separate suite verifies that heuristic mode never returns an
out-of-candidate-set result.

## 7. Interaction with capability drift

Routing trusts manifests. Manifests are only trustworthy if conformance tests
prove the implementation matches (review R3). Routing therefore inherits the
requirement: **an agent without passing conformance tests is not a routing
candidate.**

## 8. Failure modes

| Failure | Behaviour |
| --- | --- |
| Registry unavailable | fail closed — no routing, no dispatch |
| Selection component errors/times out | fall back to deterministic precedence (never to "any agent") |
| Selection returns unknown agent | `RoutingFailure` + audit as an anomaly |
| All candidates quarantined | `NoCapableAgent`, honest user message |
| Manifest/version skew | agent excluded from candidates, surfaced at startup |

## 9. Tests required

1. Hostile content in the target payload does not change the selected agent.
2. Selection output outside the candidate set ⇒ hard failure.
3. Deterministic precedence produces identical results across runs and process
   restarts.
4. Duplicate capability claims are rejected at registration.
5. Routing cannot select an agent whose manifest declares a *higher* tier than
   the task's determined tier.
6. Reroute budget exhausts to `NoCapableAgent` rather than looping.
7. Quarantined agent never appears as a candidate.
8. Authorization still denies after routing (routing is not an approval).
