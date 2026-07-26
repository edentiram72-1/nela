# Coding Agent Ecosystem

Expands `coding_agent_spec.md` into six specialized agents. The split exists
for a safety reason, not an organizational one: **the agent that writes code
must never be the agent that approves it**, and the agent that plans must not
be the agent that pushes.

Companion: `permission_model.md`, `multi_agent_orchestration.md`.

---

## 1. The six agents

| Agent | Role | Max tier | Can it merge? |
| --- | --- | --- | --- |
| **Coding Planner** | decomposes a goal into a change plan | T0 (+T1 to write the plan) | no |
| **Coding Worker** | edits code, runs tests locally | T1 | no |
| **Code Review Agent** | critiques a diff | T0 | no |
| **QA Agent** | verifies behaviour, coverage, regressions | T1 | no |
| **Git Agent** | branches, commits, pushes, opens PRs | T2 | **never to protected** |
| **Documentation Agent** | updates docs, handoff, decisions | T1 | no |

No agent in this table can merge to a protected branch. That authority stays
with a human at 1.0, 2.0 and 3.0 — it is the permanent ceiling
(`ai_system_roadmap.md`).

## 2. Coding Planner

**Responsibilities:** read the repo (T0), consult project memory for
architecture facts and conventions, produce a **change plan**: files to touch,
rationale per file, expected test impact, risk classification, rollback
strategy. Writes the plan as an artifact (T1) so it is reviewable *before* any
code changes.

**Never:** edits source, runs side-effecting commands, chooses to skip review.

**Key rule:** a plan touching `RISKY_PATHS` (auth, permissions, migrations,
CI, lockfiles, the audit log, the permission engine itself) is marked risky at
plan time, which forces a human reviewer later. Risk is declared early, not
discovered at PR time.

## 3. Coding Worker

**Responsibilities:** execute an approved plan. Minimal, localized edits;
pre-image snapshot per file; run tests and linters in a sandboxed subprocess
with no network.

**Tier discipline:** everything the Worker does is T1 — reversible, local,
unpublished. It cannot commit, cannot push, cannot install dependencies
(that is T2 and belongs to the Git Agent with confirmation).

**Bug-fix loop:** reproduce with a failing test → localize → minimal fix →
green → hand to Review. If reproduction fails, it says so; it does not guess.
A fix not covered by a test is labelled *unverified* and cannot be presented
as done.

**Scope:** project directory only, canonicalized; no writes outside; no edits
to manifests, policy, or audit code (those are risky paths requiring the full
human path).

## 4. Code Review Agent

**Responsibilities:** review the Worker's diff before any human sees it.
Checks correctness, scope creep against the plan, security (secret patterns are
a hard block), adherence to `coding_rules.md`, architecture fit against project
memory, and test adequacy.

**Output:** structured findings — severity, file reference, reasoning,
recommended action — the same format used in Claude's reviews, so the two are
comparable and interchangeable.

**Independence rules:**
- Cannot review a diff it authored (enforced by the orchestrator, not by
  convention).
- Cannot approve-and-merge; it annotates.
- **Zero findings on a non-trivial diff is itself flagged** for human
  attention — a review that never objects is not a review.

## 5. QA Agent

**Responsibilities:** full suite + coverage on the proposed branch; add missing
tests for changed behaviour; regression-gate against the base branch.

**Gates it enforces:**
- pass count must not drop versus base
- coverage must not drop on changed files
- changed behaviour without a test ⇒ blocked
- for agents touching the OS or permissions, safety-boundary tests are
  **mandatory** — conformance tests proving scope and tier (review finding R3)

QA is independent of the Worker for the same reason Review is: the writer does
not grade the work.

## 6. Git Agent

The only T2 agent in the family, and the only one holding credentials.

**Reversible-by-default:**

| Wants to | Does instead |
| --- | --- |
| force-push | new branch + PR |
| rewrite history | revert commit |
| merge to protected | PR + human gate |
| delete branch | leave it |

**Credentials:** receives a scoped, short-lived token minted per operation from
the secrets broker — never the raw PAT (`permission_model.md` §5). A secret
detected in staged content is a hard block, not a warning.

**Confirmation binding:** the confirmation the user gives is bound to a hash of
the exact commit/push/PR parameters (review finding P2). Changing the branch,
remote, or content after approval invalidates it.

## 7. Documentation Agent

**Responsibilities:** keep `docs/` truthful — update architecture docs when
behaviour changes, append to `docs/ai_handoff.md`, record decisions in
`docs/decisions.md`, refresh module READMEs.

This agent exists because documentation drift is the failure mode this project
has already demonstrated (a README describing a pre-Phase-1 skeleton, a branch
listed as current in one section and superseded in another). Automating the
update is cheaper than repeatedly discovering the drift.

**Constraint:** it documents what *is*, never what is *planned*. It may not
mark a task done; it records what the audit log and test results show.

## 8. Approval flow end to end

```text
goal
 └─ Planner → change plan (T1 artifact) ─── risky? → human review of the plan
     └─ Worker → edits + local tests (T1, snapshotted)
         ├─ Review Agent → findings (T0)
         └─ QA Agent → suite, coverage, regressions (T1)
             └─ both green?
                 └─ Git Agent → branch + commit + push + PR (T2, confirmed)
                     └─ Documentation Agent → docs + handoff (T1)
                         └─ HUMAN → merge   ← always
```

Any red gate returns to the Worker with structured findings. Three failed
cycles on the same task escalates to a human rather than looping.

## 9. Repository scope & branch strategy

**Scope tiers by repo trust:**

| Repo class | Allowed | Notes |
| --- | --- | --- |
| NELA's own repo | 1.0 onward | the only repo at 1.0 |
| Allowlisted user repos | 2.0 onward | explicit per-repo grant, expirable |
| Anything else | never | not in scope = T4 |

**Branch strategy** (mirrors the existing convention):
- `feature/NELA-XXXX-<slug>` — one task per branch, cut from `develop`
- `fix/`, `docs/` prefixes for their kinds
- **Protected:** `main`, `develop`, `release/*` — never in any agent's write
  scope; agents open PRs against them
- Agents never reuse a branch across tasks; one task, one branch, one PR

**Merge policy:**
- PR requires: Review Agent findings addressed + QA green + human approval
- Risky-path PRs require a **human** reviewer; the Review Agent alone cannot
  clear them
- No agent self-merges, at any version, ever
- Merge to `main` is release-only, via the consolidation process

## 10. Rollback

- Every Worker edit carries a pre-image token; rollback is LIFO within a scope
  (review finding X2).
- Git-level rollback prefers `revert` over history rewriting.
- A merged PR is rolled back by a revert PR through the same gates — never by a
  force-push.
- The kill switch's bulk rollback covers uncommitted Worker edits; committed
  work is rolled back through Git, deliberately, so history stays honest.

## 11. Security summary

1. Writer ≠ reviewer ≠ verifier, enforced by the orchestrator.
2. Only one agent holds credentials, and only as short-lived scoped tokens.
3. Only one agent has T2, and it cannot touch protected branches.
4. Secrets in staged content are a hard block.
5. Risky paths force a human into the loop at plan time.
6. Untrusted repo content never influences routing or authorization
   (`agent_routing_spec.md` §3) — a README cannot instruct the pipeline.
7. Every gate result is audited with the task's correlation id.
