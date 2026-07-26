# NELA OS — Branch Consolidation Plan

Paste into `docs/ai_inbox.md` under "Ready For Codex". Written per the inbox
item template.

---

## Consolidate all feature branches into develop and main

- Owner: Codex
- Requester: User (plan authored by Claude)
- Branch: n/a — this task operates across branches
- Status: ready
- Type: implementation

### Goal

`main` still contains only the day-one skeleton (1 commit). All real work —
Phase 1 Brain, the confirmation fix, Desktop Agent V1, UI foundation, the AI
Inbox — lives on unmerged feature branches, and three Claude deliverable drops
(memory subsystem, visual identity, personality/language) are not in the
repository at all. Consolidate everything into `develop`, then release
`develop → main` with a version tag.

### Context

- Review findings: `docs/claude_review_findings.md`, Claude inbox review
  (2026-07-23), `CODEX_HANDOFF.md`, `APPLY_THIS_DROP.md`.
- Known task-id collision: `NELA-0005` is used by both
  `intent-matching-hardening` (in findings) and `desktop-agent-v1` (branch).
  Resolve during this task: reassign the intent-matching task a new id and
  fix the reference in `claude_review_findings.md`.
- Branch lineage is unverified — before merging, run
  `git merge-base` between consecutive branches to confirm each wave-2+ branch
  contains its predecessor; if a branch was cut from an older base, rebase it
  onto the freshly merged `develop` instead of merging blind.

### Plan

**Preparation**

```bash
git fetch --all --prune
git checkout develop || git checkout -b develop origin/main
python3 -m unittest discover -s tests   # baseline; record the count
```

**Wave 1 — safe merges (reviewed, no conditions)**

Order matters; test gate after each merge (`python3 -m unittest discover -s
tests` must pass before proceeding; record the test count each time).

```bash
git merge --no-ff feature/NELA-0001-foundation-architecture
git merge --no-ff feature/NELA-0002-confirmation-deadlock
git merge --no-ff feature/NELA-0007-ai-inbox
```

Conflict policy: prefer the later branch for code; for `docs/ai_handoff.md`
concatenate both sides chronologically instead of choosing.

**Wave 2 — Desktop Agent V1, after fixing review conditions**

On `feature/NELA-0005-desktop-agent-v1` (or a fixup branch off it), before
merging:

1. **D1:** catch `subprocess.TimeoutExpired` / `OSError` in
   `SubprocessDesktopCommandRunner.run` (or `DesktopAgent.execute`), returning
   `AgentResult(False, ...)`. Additionally wrap `agent.execute(command)` in
   try/except inside `AgentDispatcher.dispatch`, emitting `TaskFailed` —
   contract-wide protection.
2. **D2:** resolve the `wait_until_ready` mismatch — either implement a
   bounded read-only `wait_until_ready` in `DesktopAgent` (poll `_is_running`
   with deadline) or stop emitting it for desktop targets in
   `Planner._media_tasks`. Add a test for the PlayMedia-via-desktop path.
3. **D3 (recommended):** planner marks `CloseApplication` intents
   `requires_confirmation=True` until the permission policy exists.

Then `git merge --no-ff` into `develop`; test gate.

**Wave 3 — Claude deliverable drops (new branches off updated develop)**

Apply in this order, each per its own instruction file, each with a test gate:

1. Memory subsystem — `CODEX_HANDOFF.md` Part 1 → branch
   `feature/NELA-0012-memory-subsystem`. Acceptance: all pre-existing tests +
   53 memory tests pass with zero changes under `brain/`.
2. Visual identity — `CODEX_HANDOFF.md` Part 2 → branch
   `feature/NELA-0011-visual-identity` (docs + assets only; the
   rendering-backend DEC is required before wiring, not before landing files).
3. Personality & language — `APPLY_THIS_DROP.md` → branch
   `feature/NELA-0014-personality-language` (validated JSON; the Language
   Engine implementation is a separate follow-up task).

Merge each into `develop` after its gate passes.

**Wave 4 — UI foundation (conditional)**

`feature/NELA-0006-ui-foundation` merges only after a DEC records the
rendering-backend decision (Tkinter vs webview — see Claude inbox review U1).
If the decision is webview: merge the state layer (`ui/state.py`,
`ui/events.py`, `ui/router.py`, tests) and hold `ui/window.py` + components
for rework. Extend `EyeState` to the 11 canonical states (U2) in the same
change.

**Release**

```bash
git checkout main && git merge --no-ff develop
git tag v0.1.0-brain-foundation
git push origin main develop --tags
```

Refresh `README.md` on main as part of the release (the current one describes
the pre-Phase-1 skeleton), fixing the contradictions already flagged: single
source of truth for the active branch, numeric test count, task-id collision.

### Acceptance Criteria

- [ ] `develop` contains waves 1–3; each merge passed the full test suite.
- [ ] Test count recorded in `docs/ai_handoff.md` after every wave (numbers).
- [ ] D1 + D2 fixed and tested before the Desktop Agent merge.
- [ ] NELA-0005 id collision resolved in docs.
- [ ] `main` tagged `v0.1.0-brain-foundation`; README updated.
- [ ] `docs/ai_inbox.md` lanes updated (this item → done; UI foundation →
      blocked-on-DEC unless decided).

### Handoff Notes

After completion, the highest-value next tasks remain, in order: task
idempotency metadata, permission policy layer, event-bus hardening, capability
registry — all pre-conditions for the next real agent (browser/files).
Claude review checkpoints: after wave 2 (desktop fixes) and after the
rendering-backend DEC.
