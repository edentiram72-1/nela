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

#### UI Foundation Review

- Owner: Claude
- Requester: Codex
- Branch: `feature/NELA-0006-ui-foundation`
- Status: ready
- Focus: Review UI infrastructure only. Do not redesign inside this branch.
- Links:
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/ui/state.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/ui/events.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/ui/router.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/ui/theme.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/ui/window.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/tests/test_ui_state.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0006-ui-foundation/docs/ai_handoff.md

#### Desktop Agent V1 Safety Review

- Owner: Claude
- Requester: Codex
- Branch: `feature/NELA-0005-desktop-agent-v1`
- Status: ready
- Focus: Review macOS lifecycle safety, supported app boundaries, and whether real side effects are appropriately constrained.
- Links:
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0005-desktop-agent-v1/agents/desktop/agent.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0005-desktop-agent-v1/tests/test_desktop_agent.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0005-desktop-agent-v1/brain/planner.py
  - https://github.com/edentiram72-1/nela/blob/feature/NELA-0005-desktop-agent-v1/docs/ai_handoff.md

### Ready For Codex

Items ready for implementation.

#### Claude Review Fixes

- Owner: Codex
- Requester: Claude
- Branch: `feature/NELA-0012-claude-review-fixes`
- Status: in progress
- Scope:
  - Catch Desktop Agent `TimeoutExpired`.
  - Add Dispatcher exception boundary around `agent.execute()`.
  - Support Desktop `wait_until_ready`.
  - Require confirmation for `CloseApplication`.
  - Record the UI WebView host decision.
  - Update Inbox and Handoff.

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

#### AI Inbox Workflow

- Owner: Codex
- Requester: User
- Branch: `feature/NELA-0007-ai-inbox`
- Status: done
- Scope:
  - Add this inbox document.
  - Add GitHub Issue template for AI collaboration inbox items.
  - Update handoff and documentation.

### Ready For ChatGPT

Items waiting for architecture or coordination approval.

- None.

### Blocked

Items blocked by missing information, credentials, assets, or user approval.

- None.

### Done

Completed inbox items.

- AI Inbox Workflow: `docs/ai_inbox.md` and GitHub Issue template created.

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
