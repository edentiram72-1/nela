# AI Inbox

This file is the shared GitHub inbox for Claude, Codex, ChatGPT, and future AI assistants working on NELA OS.

GitHub is the collaboration layer. Do not create direct communication channels between assistants.

## Purpose

Use this inbox to track review requests, implementation requests, blockers, handoffs, and decisions that need attention from a specific AI role.

## Roles

### Claude

Owns:

- Brand identity
- Eye design
- UI review
- UX review
- Animations
- Design system
- Architecture and documentation review
- Edge-case and risk analysis

Claude should usually receive direct `blob/` links or a generated review bundle because automated access to GitHub `tree/` and `compare/` pages may be blocked.

### Codex

Owns:

- Brain implementation
- Agents
- Desktop control
- Voice infrastructure
- Memory infrastructure
- Automation
- Tests
- Refactors
- Documentation updates tied to implementation

Codex must keep changes modular, update `docs/ai_handoff.md`, and avoid redesigning Claude-owned UI.

### ChatGPT

Owns:

- Architecture definition
- System design
- Development coordination
- Major structural approval
- Roadmap shaping

## Inbox Lanes

### New

Items that need triage.

- None.

### Ready For Claude

Items waiting for Claude review or design input.

#### Consolidated Foundation Release Review

- Owner: Claude
- Requester: Codex
- Branch: `develop`, then `main` after release merge
- Status: ready
- Focus: Verify that the consolidated foundation matches the intended architecture and that no direct Claude integration was introduced.
- Links:
  - https://github.com/edentiram72-1/nela/blob/develop/docs/ai_handoff.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/ai_inbox.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/architecture.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/claude_review_findings.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/decisions.md

#### Hebrew Language And Voice Foundation Review

- Owner: Claude
- Requester: Codex
- Branch: `develop`, then `main` after release merge
- Status: ready
- Focus: Review language/personality infrastructure and Hebrew pack extensibility. Claude owns final tone and personality; Codex should keep Brain code semantic and phrase-free.
- Links:
  - https://github.com/edentiram72-1/nela/blob/develop/docs/language_system.md
  - https://github.com/edentiram72-1/nela/blob/develop/docs/voice_architecture.md
  - https://github.com/edentiram72-1/nela/tree/develop/language

### Ready For Codex

Items ready for implementation.

#### Phase A Safety Spine

- Owner: Codex
- Requester: Claude/User
- Branch: TBD
- Status: ready
- Type: architecture + implementation + tests
- Source specs:
  - `docs/permission_model.md`
  - `docs/nela_runtime_architecture.md`
  - `docs/multi_agent_orchestration.md`
  - `docs/ai_system_roadmap.md`
- Goal: Implement the safety foundation before any new real Agents are added.
- Ordered tasks:
  - `NELA-0004-task-idempotency`: add idempotency metadata and retry policy.
  - `NELA-0006-permission-policy`: implement the shared T0-T4 permission engine and reuse the existing confirmation flow.
  - `NELA-0007-event-bus-hardening`: add subscriber isolation, bounded history, and correlation/trace conventions.
  - `NELA-0008-capability-registry`: load declared Agent capability manifests; unknown actions fail closed.
  - `NELA-0009-plan-executor`: move execution semantics toward async/cancellable plan execution.
  - `NELA-0016-audit-log-and-kill-switch`: add append-only action audit records and global halt/revoke behavior.
  - `NELA-0017-agent-runtime-lifecycle`: add runtime health, lifecycle, backpressure, and worker boundaries.
- Safety note: Cyber, Coding, Research, Browser, Terminal, Files, and communication Agents must not gain new real side effects before the Safety Spine is implemented and tested.

#### Task Idempotency

- Owner: Codex
- Requester: Claude
- Branch: TBD
- Status: ready
- Type: architecture + implementation + tests
- Scope:
  - Add idempotency metadata to `Task` and `AgentCommand`.
  - Prevent automatic retries for non-idempotent or unknown side-effecting tasks.
  - Use command IDs as idempotency keys where Agents support them.
  - Add tests before enabling real Terminal, Browser, Files, or communication Agents.

#### Permission Policy

- Owner: Codex
- Requester: Claude
- Branch: TBD
- Status: ready
- Type: architecture + implementation + tests
- Scope:
  - Add a central policy layer for destructive, external, private-data, system-setting, and communication actions.
  - Keep confirmation behavior consistent across Agents.
  - Avoid Agent-specific permission logic inside the Brain.

#### WebView UI Host Selection

- Owner: Codex
- Requester: Claude
- Branch: TBD
- Status: ready
- Type: architecture + implementation
- Scope:
  - Choose a WebView-compatible host for `design/nela_living_eye.html`.
  - Keep `UIStateManager`, `UIEventBridge`, and `UIRouter`.
  - Replace the placeholder Tkinter visual shell without redesigning Claude's assets.

### Ready For ChatGPT

Items waiting for architecture or coordination approval.

- None.

### Blocked

Items blocked by missing information, credentials, assets, or user approval.

#### Memory Subsystem Deliverable

- Owner: Codex
- Requester: Claude/User
- Branch: TBD
- Status: blocked
- Type: implementation
- Blocker: `nela-memory-subsystem.zip` was not found in `/Users/edentiram/Downloads`, `/Users/edentiram/Downloads/files`, or the current attachment directory.
- Next action: User provides the zip, then Codex creates a dedicated memory subsystem branch and validates it separately.

#### Advanced Agent Implementation

- Owner: Codex
- Requester: Claude/User
- Branch: TBD
- Status: blocked
- Type: implementation
- Blocker: The Safety Spine is specification-only and not implemented yet.
- Scope: Coding Agent, Cyber Agent, Research Agent, advanced orchestration, and any new real side-effecting Agent capabilities.
- Next action: Complete Phase A Safety Spine first.

### Done

Completed inbox items.

- AI Inbox Workflow: `docs/ai_inbox.md` and GitHub Issue template created.
- UI Foundation: merged into `develop`.
- Desktop Agent V1: merged into `develop`.
- Living Eye Visual Identity: merged into `develop`.
- Claude Review Fixes: merged into `develop`.
- Hebrew Language And Voice Foundation: merged into `develop`.
- Confirmation Deadlock Fix: merged into `develop`.

## Inbox Item Template

Use this format inside this file or in a GitHub Issue created from the AI Collaboration Inbox template.

```markdown
## Title

- Owner: Claude | Codex | ChatGPT
- Requester:
- Branch:
- Status: new | ready | in progress | blocked | done
- Type: review | implementation | architecture | design | docs | bug | test

### Goal

Describe the requested outcome.

### Context

Important links, prior decisions, and relevant files.

### Acceptance Criteria

- [ ]

### Handoff Notes

What should the next AI assistant know?
```

## Rules

- Use one focused inbox item per task.
- Prefer direct GitHub `blob/` links for Claude.
- Use generated bundles for broad reviews.
- Update `docs/ai_handoff.md` after significant work.
- Record major architecture decisions in `docs/decisions.md`.
- Do not use this file for secrets, credentials, private personal data, or API keys.
