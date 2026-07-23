# Architecture Decisions

This file records significant architecture and process decisions for NELA OS.

Use a new entry for every decision that changes module boundaries, project structure, collaboration rules, or long-term direction.

## Decision Template

```text
ID:
Date:
Status:
Context:
Decision:
Consequences:
Related files:
```

## Decisions

### DEC-0001: Use GitHub As The Multi-AI Collaboration Layer

**Date:** 2026-07-22
**Status:** Accepted

**Context:** NELA OS needs to support collaboration between Codex, Claude, ChatGPT, and future AI assistants. Direct assistant-to-assistant communication would add complexity and fragility.

**Decision:** Use GitHub as the shared source of truth. Assistants collaborate through repository files, branches, commits, pull requests, issues, and `docs/ai_handoff.md`.

**Consequences:**

- Every assistant can clone the repository and understand the current state.
- Work is traceable through Git history and documentation.
- Merge conflicts are reduced by keeping modules independent.
- No direct communication channel with Claude is required.

**Related files:**

- `README.md`
- `docs/ai_handoff.md`
- `docs/coding_rules.md`

### DEC-0002: Keep Top-Level Modules Independent

**Date:** 2026-07-22
**Status:** Accepted

**Context:** Multiple assistants may work on different features at the same time. Coupled modules increase the risk of merge conflicts and accidental regressions.

**Decision:** Use clear top-level folders for major capabilities and keep each feature inside the smallest relevant module.

**Consequences:**

- Assistants can work in separate folders with fewer conflicts.
- Shared abstractions must be deliberate and documented.
- Cross-module changes require extra review and handoff notes.

**Related files:**

- `docs/architecture.md`
- `docs/coding_rules.md`

### DEC-0003: Make The Brain Agent-Neutral And Event-Driven

**Date:** 2026-07-22
**Status:** Accepted

**Context:** Phase 1 requires a production-ready Brain foundation. The Brain must think, plan, remember, and delegate without directly performing actions or embedding service-specific behavior.

**Decision:** The Brain owns conversation flow, intent recognition, decision making, planning, context, memory orchestration, and dispatch coordination. Execution remains inside independent Agents. Major lifecycle changes are published as Events.

**Consequences:**

- New Agents can register dynamically through `AgentDispatcher`.
- The Brain can support future plugins without hardcoded Agent logic.
- Testing can focus on Brain behavior without real desktop or service integrations.
- Real action execution must be implemented in Agents during later phases.

**Related files:**

- `brain/conversation.py`
- `brain/intent_router.py`
- `brain/planner.py`
- `brain/decision.py`
- `brain/context.py`
- `brain/dispatcher.py`
- `brain/memory_manager.py`
- `agents/base.py`

### DEC-0004: Use Review Bundles For Claude Collaboration

**Date:** 2026-07-23
**Status:** Accepted

**Context:** Claude cannot access local machine paths such as `/Users/.../nala/docs/architecture.md`. Direct assistant-to-assistant communication is also outside the intended collaboration model.

**Decision:** Add a Claude collaboration Agent and export script that prepare a Markdown review bundle. The bundle can be pasted into Claude, uploaded to Claude, or attached to a GitHub pull request.

**Consequences:**

- Claude can review the same source of truth without direct local access.
- Codex can regenerate a current review bundle after significant changes.
- Review focus and required files remain explicit and traceable.
- The system still avoids direct communication channels between AI assistants.

**Related files:**

- `agents/claude/agent.py`
- `scripts/export_claude_review_bundle.py`
- `docs/claude_review_bundle.md`
- `docs/ai_handoff.md`

### DEC-0005: Store Original Intent In Pending Confirmations

**Date:** 2026-07-23
**Status:** Accepted

**Context:** `NELA-0002-confirmation-deadlock` fixes a deterministic deadlock where follow-up answers to confirmation questions were classified as new input before `resolve_confirmation()` could run. When a user confirms, the Brain must continue the original blocked request without storing a full Plan too early.

**Decision:** Store the original `Intent` in `PendingConfirmation.metadata`. On affirmative confirmation, the Conversation Engine resolves the confirmation, marks that Intent as confirmed, and creates a fresh Plan from the original Intent. The Planner and Agent contract remain unchanged.

**Consequences:**

- The Brain can resume the blocked request after `yes`, `confirm`, or equivalent replies.
- Plans are still created only after approval, reducing stale Plan state.
- Confirmation answer routing stays in `ConversationEngine`; `DecisionEngine` remains pure.
- Future durable confirmation storage will need serializable Intent metadata.

**Related files:**

- `brain/conversation.py`
- `brain/context.py`
- `core/events.py`
- `tests/test_conversation_confirmations.py`

### DEC-0006: Add Living Eye As The Authoritative Visual Identity Artifact

**Date:** 2026-07-23
**Status:** Accepted

**Context:** Claude delivered the NELA visual identity package: a dependency-free Living Eye prototype, app icon, macOS menu-bar icon, and design system. The current Codex-owned UI shell is Tkinter-based and was intentionally built as infrastructure without final visual design.

**Decision:** Store Claude's visual identity artifacts under `design/` and `docs/design_system.md` without restyling them. Keep the current Tkinter shell as the application infrastructure for now, but align `UIEventBridge` and `EyeState` with the design-system state contract so a future WebView/Electron/Tauri host can drive the Living Eye with the same Brain events.

**Consequences:**

- Claude's design system becomes the authoritative source for NELA's face, motion, icons, and visual identity.
- Brain architecture remains unchanged; UI state follows Brain events through the existing Event Bus subscriber.
- The current Tkinter placeholder does not render the full HTML/SVG Living Eye yet.
- A future UI-hosting decision is still needed before embedding `design/nela_living_eye.html` into the live desktop shell.

**Related files:**

- `design/nela_living_eye.html`
- `design/nela_app_icon.svg`
- `design/nela_menubar_icon.svg`
- `docs/design_system.md`
- `ui/events.py`
- `ui/state.py`
- `ui/window.py`

### DEC-0007: Host The Living Eye In A WebView-Compatible UI Backend

**Date:** 2026-07-23
**Status:** Accepted

**Context:** Claude reviewed the UI foundation and confirmed that the state, router, and Event Bridge layers are correctly renderer-neutral. The blocking issue is the render backend: Tkinter cannot faithfully render the authored Living Eye, which depends on HTML, SVG filters such as `feTurbulence`, CSS variables, gradients, glow, font loading, and motion rules from `docs/design_system.md`.

**Decision:** Keep `UIStateManager`, `UIEventBridge`, `UIRouter`, theme tokens, and animation hooks as Codex-owned infrastructure. Treat the current Tkinter shell as a temporary placeholder. The production visual shell should move to a WebView-compatible host that can load `design/nela_living_eye.html` directly and synchronize state through one state bridge. Candidate hosts include a lightweight Python WebView, Tauri, Electron, or another native wrapper that can embed the original HTML/SVG without redesigning it.

**Consequences:**

- Claude's visual identity remains authoritative and is not reimplemented as a degraded Tkinter canvas approximation.
- Brain architecture remains unchanged because UI state is already event-driven.
- Future UI work should replace `ui/window.py` and visual components, not `ui/state.py`, `ui/events.py`, or `ui/router.py`.
- The `psychedelic` visual direction lives primarily inside the Living Eye. App chrome should remain quiet and token-driven.
- A follow-up task must choose the concrete WebView host before building production UI components.

**Related files:**

- `design/nela_living_eye.html`
- `docs/design_system.md`
- `ui/window.py`
- `ui/state.py`
- `ui/events.py`
- `ui/router.py`
- `ui/theme.py`
