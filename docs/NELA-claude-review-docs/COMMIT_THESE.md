# COMMIT THESE — Claude review docs (item 2 of your request)

You asked me not to leave review work only in chat. This folder contains every
review/architecture doc I have produced, commit-ready. Claude cannot run git;
apply locally.

## Files → destination

All 18 files go to `docs/`:

| File | What it is |
| --- | --- |
| `claude_open_findings.md` | **the tracker** — single source of truth for every finding + status |
| `sprint2_implementation_review.md` | actual-code review of Safety Spine @860fbd9 (A1–T2 verdicts) |
| `sprint2_architecture_review.md` | adversarial design review (the 8 findings originate here) |
| `safety_spine_verification_criteria.md` | mechanical PASS/FAIL criteria per finding |
| `permission_model.md` | capability tiers, scope, audit, kill switch, secrets |
| `nela_runtime_architecture.md` | runtime + 15-system map |
| `runtime_operations.md` | lifecycle, queue, recovery, health, resources |
| `multi_agent_orchestration.md` | task queue, orchestrator, PM agent |
| `agent_routing_spec.md` | two-gate routing, injection resistance |
| `auth_session_lock_model.md` | bridge auth, scoped sessions, lock mode |
| `coding_agent_spec.md` / `coding_agent_ecosystem.md` | coding agent family |
| `cyber_agent_spec.md` / `cyber_agent_architecture_v2.md` | defensive cyber design + lab isolation |
| `phase_a_safety_spine_tasks.md` | A-01..A-13 implementation tasks |
| `ai_system_roadmap.md` | 25% → 1.0 → 2.0 → 3.0 |
| `claude_review_findings.md` | original Phase 1 Brain findings |
| `nela_merge_plan.md` | branch consolidation plan |

If any same-named file already exists in `docs/`, diff before overwriting — the
versions here are the latest.

## Commit

```bash
cd ~/Documents/nala
git checkout develop && git pull
git checkout -b docs/NELA-claude-review-docs
cp <this folder>/docs/*.md docs/
git add docs/*.md
git commit -m "Add Claude architecture and safety review docs"
git push -u origin docs/NELA-claude-review-docs
```

Merge this into `develop` independently of any code branch — it is docs-only,
zero risk, and stops the review work from being stranded.

## After committing, update docs/ai_handoff.md

Append: "Claude review docs committed on docs/NELA-claude-review-docs. Open
findings tracked in docs/claude_open_findings.md — R1 and K1 verification are
merge-blockers; cyber agents pending defensive-only verification."
