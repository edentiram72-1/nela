# Coding Agent Specification

Covers the coding family: **Coding Agent** (writes code), **Code Review Agent**
(critiques it), **Test/QA Agent** (verifies it), **Git/GitHub Agent** (moves
it). All four share the manifest/tier system in `permission_model.md` and never
touch protected branches directly.

Status: specification only.

---

## 1. Coding Agent — purpose & boundaries

Turns a well-scoped task into a reviewed, tested change proposed as a PR. It
proposes; humans (and the Review/QA agents) dispose. It never merges to a
protected branch and never pushes without confirmation.

**Tier map (from its manifest):**

| Action | Tier | Notes |
| --- | --- | --- |
| read_repo, read_file, inspect_arch | T0 | free, logged |
| run_tests, run_linter, format | T1 | sandboxed subprocess, no network |
| edit_file, create_branch, stage | T1 | scope = project dir only |
| commit | T2 | confirm |
| push_branch (non-protected) | T2 | confirm |
| open_pull_request | T2 | confirm |
| install_dependency | T2 | sandboxed, confirm, lockfile diff shown |
| edit outside project / push protected | T4 | forbidden |

## 2. Inspecting repositories & understanding architecture

- **Cold read (T0):** enumerate structure, read entry points, config, tests,
  and docs. Build a dependency-direction map.
- **Warm read (memory):** reuse project memory (`nela_runtime_architecture.md`
  §7) — stored architecture facts, conventions, past decisions — so the agent
  doesn't re-derive the codebase every session. New findings are written back
  (T1) as semantic facts and, for big ones, episodes.
- **Convention inference:** detect formatter, test runner, branch naming,
  commit style from the repo itself; never impose external defaults. For NELA
  itself, `docs/coding_rules.md` is authoritative.

## 3. Editing code

- Edits are **minimal and localized** — the repo's own rule ("never modify
  unrelated code") is enforced by the agent, not just hoped for.
- Every edit is preceded by a plan the user/PM can see: files, rationale,
  expected test impact.
- Pre-image snapshot per file (T1 rollback token) before writing.
- No edit outside the filesystem scope; paths canonicalized (no `../` escape).

## 4. Running tests & fixing bugs

- Test runs are T1, sandboxed (no network, resource-limited). Results are
  structured, not scraped from stdout.
- **Bug-fix loop:** reproduce (write/confirm a failing test) → localize →
  minimal fix → tests green → self-review (§7) → propose. If reproduction
  fails, the agent says so instead of guessing.
- A fix that can't be verified by a test is flagged as unverified in the PR —
  never presented as done.

## 5. Git/GitHub Agent — safe version control

Reversible-by-default. The agent prefers the operation that is easiest to
undo:

| Wants to | Does instead |
| --- | --- |
| force-push | new branch + PR |
| rewrite history | revert commit |
| direct merge to main | PR + review gate |
| delete branch | leave it; PM archives later |

- **Commits:** small, one logical change, message in repo style. Body notes the
  task id and links the plan.
- **PRs:** generated with a filled template (what/why/tests/risks), reviewers
  = Review Agent + human. Never self-merges.
- **Credentials:** receives a scoped, short-lived token per operation from the
  keychain broker — never the raw PAT (`permission_model.md` §5).
- **Coordination with Codex & Claude (DEC-0001):** the agent's unit of
  collaboration is a branch + PR + `docs/ai_handoff.md` update, exactly like
  the human-driven flow today. It does not open a direct channel to another
  AI. Claude reviews its PRs through blob links / bundles just as now.

## 6. Test/QA Agent

Independent of the Coding Agent so the writer never grades its own work.
- Runs the full suite + coverage on the proposed branch (T1).
- Adds missing tests for changed behavior; flags untested changes.
- Regression gate: compares against the base branch; a drop in pass count or
  coverage blocks the PR (mirrors the merge-plan test gates).
- Safety-boundary tests for agents that touch the OS (e.g. Desktop, Cyber)
  are mandatory, per `docs/coding_rules.md`.

## 7. Code Review Agent

The critic. Reviews the Coding Agent's diff **before** human review, so humans
see a pre-vetted change.
- Checks: correctness, scope creep, security (secret patterns → T4 block),
  adherence to `coding_rules.md`, architecture fit against project memory,
  test adequacy.
- Output: structured findings with severity + file refs — the same format
  Claude uses in its reviews, so the two are interchangeable and comparable.
- Cannot approve-and-merge; it annotates. Merge stays human (or PM policy).
- Explicitly does **not** rubber-stamp: a review with zero findings on a
  non-trivial diff is itself flagged for human attention.

## 8. Risky-change approval

An edit is "risky" (forces confirmation regardless of tier) when it touches:
security controls, auth, the permission engine, migrations, dependency
lockfiles, CI config, or anything in a `RISKY_PATHS` list. Risky changes get an
expanded PR body (blast radius, rollback plan) and a mandatory human reviewer —
the Review Agent alone can't clear them.

## 9. Failure modes

- Tests flaky/nondeterministic → agent reports instability, doesn't loop
  forever burning rate limit.
- Merge conflict with base → rebase attempt once; if unresolved, hand to human
  with a clear conflict summary.
- Scope violation attempt → blocked + audited + PM notified; repeated attempts
  → quarantine.

## 10. Roadmap fit

- **NELA 1.0:** Coding + Git agents on NELA's own repo only, everything T2 with
  confirmation, no autonomy. Human merges every PR.
- **NELA 2.0:** Review + QA agents gate PRs; PM agent sequences multi-file
  features; still human-merged for protected branches.
- **NELA 3.0:** supervised autonomy on allowlisted repos — the agent chain can
  open, review, and test a PR end-to-end; a human still holds the merge and the
  kill switch.
