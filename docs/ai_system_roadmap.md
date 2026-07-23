# NELA AI System Roadmap

From the current foundation to a supervised multi-agent AI system. Each phase
is gated: safety infrastructure lands **before** the capability it protects.

Status: planning. No implementation in this task.

---

## Baseline — where we are (~25%)

Delivered and (mostly) reviewed:
- Event-driven Brain: conversation, intent, decision, planner, context,
  dispatcher, memory orchestration.
- Confirmation workflow (NELA-0002) — the gate every higher tier reuses.
- Desktop Agent V1 (macOS app lifecycle, allowlisted) — first real agent.
- Memory subsystem (7 layers + search).
- Visual identity (living eye, 11 states) + design system.
- Personality & Hebrew language framework (117 seed phrases, engine-ready).
- Voice foundation (Carmit TTS, silent-by-default).

Not yet present — the gap to close first: **permission engine, capability
registry, idempotency metadata, event-bus hardening, async execution.** These
are prerequisites, not features, and several are already tracked review
findings.

---

## Phase A — Safety spine (bridge to 1.0)

*Nothing new gets to act until this exists.*

1. Permission & approval engine (`permission_model.md`) — tiers, scope, audit,
   kill switch, secrets broker, rollback.
2. Capability registry + agent manifests (closes review H1).
3. Task idempotency + dispatcher hardening (closes C2/C3).
4. Event-bus hardening: handler isolation, bounded history, correlation ids.
5. Async execution model in the Orchestrator (real timeouts, concurrency).

Exit criteria: every existing agent runs through the Permission Engine; audit
log records every action and refusal; kill switch verified.

---

## NELA 1.0 — Trustworthy single-agent assistant

Theme: **do a few things, safely, with a human in the loop for everything real.**

- Coding Agent + Git Agent on **NELA's own repo only**. All side effects T2 →
  confirmed. Human merges every PR.
- Defensive Cyber Agent: **passive only** — code/log/config audits + reports
  (T0/T1). No lab, no network.
- Research Agent (T0) + Browser Agent (reads T0, submits T2).
- Memory persistence backend (Phase-4 durability) so project knowledge
  survives restarts.
- UI: eye wired to the full event→state map; webview backend decided (review
  U1) and shipped.
- Language Engine live; voice opt-in.

1.0 done = NELA can research a question, audit your code, and propose a
reviewed+tested PR to its own repo, narrating status through the eye — and
cannot do anything irreversible without you.

---

## NELA 2.0 — Supervised multi-agent development

Theme: **agents cooperate on features; humans gate merges and risk.**

- Project Manager Agent decomposes features across Coding/Review/QA/Git.
- Review + QA agents gate every PR (independent of the writer).
- Bounded concurrency for independent tasks (Orchestrator worker pool).
- Coding agents on **allowlisted external repos**, still human-merged for
  protected branches.
- Isolated Cyber Lab: T3 scanning of **user-created lab targets**; educational
  CVE walkthroughs; non-destructive validation only.
- Vision Agent assisting other agents (locate UI, read screens).
- Mobile companion (status + confirmations on the go), per the product roadmap.

2.0 done = you describe a feature, NELA plans it, a chain of agents implements
and verifies it, and you review one clean PR — with the whole flow audited.

---

## NELA 3.0 — Supervised autonomy

Theme: **long-running, multi-step autonomy under a permanent human ceiling.**

- End-to-end feature delivery on allowlisted repos: open → code → review →
  test → PR, with a human holding only the merge and the kill switch.
- Continuous passive security monitoring of the user's own systems, with
  alerting. Still zero offensive capability.
- Richer Cyber Lab (multi-host scenarios) for learning.
- Multi-project PM: NELA tracks several repos/projects, surfaces priorities,
  proposes work.
- Cloud sync of project knowledge (encrypted), cross-device continuity.

3.0 non-goals (permanent): no autonomous merges to protected branches, no
offensive security, no action outside declared scope, no self-modification of
the permission engine or audit log. The ceiling does not rise with trust.

---

## Governing rules across all phases

1. **Safety before capability** — the tier gate for an action ships before the
   action does.
2. **Trust changes tone, never tier** — the Language personality warms over
   time; permissions never loosen.
3. **Everything auditable and reversible** — no capability lands without its
   audit record and rollback path.
4. **Human ceiling is permanent** — merge authority and the kill switch stay
   with the user at 3.0 exactly as at 1.0.
5. **Collaboration stays file/GitHub-based** — agents coordinate through the
   repo, never direct channels (DEC-0001).
