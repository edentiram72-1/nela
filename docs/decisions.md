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

### DEC-0008: Separate Hebrew Language Rendering From Voice Playback

**Date:** 2026-07-23
**Status:** Accepted

**Context:** Claude is designing NELA's personality, Hebrew tone, emotional behavior, and language framework. Codex needs to implement the technical foundation without inventing the final personality or hardcoding phrases inside the Brain.

**Decision:** Add a standalone `language/` subsystem for loading, validating, selecting, and rendering Hebrew language-pack phrases. Add a `VoiceAgent` that speaks the rendered text through a replaceable provider. The Brain remains semantic and agent-neutral; `core/response.py` adapts Brain turns into Hebrew text and delegates speech through the Agent Dispatcher.

**Consequences:**

- Claude can expand language packs and personality profiles without changing Brain code.
- UI and Voice receive the same rendered response text.
- Provider-specific speech code stays under `voice/providers/`.
- Voice output can run in silent mode for safe local development and tests.
- Future personality decisions must update language/personality files and documentation rather than embedding wording in Brain modules.

**Related files:**

- `language/`
- `agents/voice/agent.py`
- `voice/providers/`
- `core/response.py`
- `docs/language_system.md`
- `docs/voice_architecture.md`

### DEC-0009: Consolidate Foundation Feature Branches Through Develop

**Date:** 2026-07-23
**Status:** Accepted

**Context:** NELA OS had several linear feature branches covering the Brain foundation, confirmation handling, Desktop Agent V1, UI foundation, AI Inbox, Living Eye visual identity, Claude review fixes, and Hebrew language/voice foundation. Keeping the working baseline split across many branches made it harder for Claude, ChatGPT, and Codex to review the same current state.

**Decision:** Use `develop` as the integration branch for the first foundation release, merge the completed feature branches into it, validate the combined system, then merge `develop` into `main` as the stable baseline.

**Consequences:**

- GitHub becomes easier to use as the shared source of truth.
- Claude can review `develop` or `main` instead of chasing multiple feature branches.
- Future work should start from `develop` after the release merge.
- Blocked work, such as the missing memory subsystem zip, remains outside the release until its source artifact is available.

**Related files:**

- `docs/ai_handoff.md`
- `docs/ai_inbox.md`
- `README.md`
- `README.he.md`

### DEC-0010: Speech Events Own Voice Eye State Transitions

**Date:** 2026-07-23
**Status:** Accepted

**Context:** Integration Sprint 1 required the end-to-end flow `Brain -> Language Engine -> UI -> Voice Agent` to drive the Eye through speaking states. The Voice Agent publishes both speech lifecycle events and normal Dispatcher task lifecycle events. If the UI treats the Voice Agent's `TaskCompleted` as a generic success state, it can override `SpeechCompleted -> IDLE`.

**Decision:** The UI Event Bridge treats `SpeechStarted`, `SpeechCompleted`, and `SpeechFailed` as the authoritative events for voice-output Eye state. `TaskCompleted` from the `voice` Agent does not override the Eye state after speech completion.

**Consequences:**

- Voice output maps cleanly to `SPEAKING`, `IDLE`, and `ERROR`.
- The same Voice Agent can still participate in Dispatcher task lifecycle telemetry.
- Non-voice task completion still maps to `SUCCESS`.
- Future UI hosts can animate the Living Eye from speech events without depending on provider-specific voice code.

**Related files:**

- `ui/events.py`
- `ui/state.py`
- `core/events.py`
- `agents/voice/agent.py`
- `tests/test_ui_state.py`

### DEC-0011: Treat Claude Language Drop As Authoritative Content

**Date:** 2026-07-24
**Status:** Accepted

**Context:** Claude delivered `nela-language-drop-final.zip` with a complete Hebrew personality and language package: 117 Hebrew variants across 31 categories, 3 personality presets, conversation rules, tone rules, Hebrew language guidance, and a language-pack schema. The existing Codex language seed pack used a simpler list-based format and older category names.

**Decision:** Store Claude's language and personality files as the authoritative content source. Keep the Brain semantic and phrase-free. Update the Language Engine compatibility layer so it can load Claude's `pack/categories/variants` format while preserving support for the earlier list-based internal pack shape where useful.

**Consequences:**

- Claude owns final Hebrew tone, personality, and phrase content through data files and documentation.
- Codex owns the engine, validation, rendering, and integration points.
- `core/response.py` maps semantic Brain outcomes to Claude categories such as `desktop.launch`, `media.play`, `learning.saved`, `success.short`, and `error.recovering`.
- The engine now preserves Claude metadata such as `speech_text`, `eye_state`, `gender_tier`, `min_stage`, `max_per_session`, `cooldown_group`, `time_of_day`, `humor`, and personality `pack_overrides`.
- Full schema behavior, including richer anti-repetition, humor budgeting, time-of-day filtering, memory-backed relationship stage, and phrase event observability, remains future work.

**Related files:**

- `docs/personality_bible.md`
- `docs/hebrew_language_guide.md`
- `docs/tone_of_voice.md`
- `docs/conversation_rules.md`
- `docs/language_compat_report.md`
- `language/pack_schema.md`
- `language/pack_format.py`
- `language/loader.py`
- `language/models.py`
- `language/renderer.py`
- `language/selector.py`
- `language/validator.py`
- `core/response.py`
- `tests/test_language_engine.py`

### DEC-0013: Make The Permission Model The Agent Safety Spine

**Date:** 2026-07-24
**Status:** Accepted

**Context:** NELA is expected to evolve into a multi-agent system with Coding, Cybersecurity, Research, orchestration, runtime lifecycle, and future external-action Agents. These capabilities cannot be safe if every Agent invents its own approval, scope, retry, and refusal rules.

**Decision:** Treat `docs/permission_model.md` as the shared safety spine for future Agents. Every Agent action must declare a static capability tier from `T0` through `T4`; the system must never infer tiers at runtime. Unknown or unclassifiable actions fail closed as `T4`. The permission model gates future Coding, Cyber, Research, Browser, Terminal, Files, and communication Agent capabilities before execution.

**Consequences:**

- `NELA-0006-permission-policy`, `NELA-0008-capability-registry`, `NELA-0004-task-idempotency`, `NELA-0007-event-bus-hardening`, and `NELA-0009-plan-executor` become Phase A prerequisites before advanced real Agents.
- Cybersecurity capabilities remain defensive, authorized, and lab-isolated by design.
- Relationship/trust state can change tone but must not lower a capability tier.
- The Brain stays semantic and agent-neutral; the Dispatcher/Runtime boundary owns authorization before `agent.execute()`.
- Future specifications should reference the shared permission model instead of duplicating safety rules.

**Related files:**

- `docs/permission_model.md`
- `docs/nela_runtime_architecture.md`
- `docs/coding_agent_spec.md`
- `docs/cyber_agent_spec.md`
- `docs/multi_agent_orchestration.md`
- `docs/ai_system_roadmap.md`
- `docs/ai_inbox.md`

### DEC-0014: Gate Agent Execution At The Dispatcher Boundary

**Date:** 2026-07-24
**Status:** Accepted

**Context:** Sprint 2 requires a Permission Engine that becomes the single
gateway before every Agent execution without redesigning the Brain or building
new real Agents.

**Decision:** Implement `permissions/` as an independent subsystem and integrate
it at `AgentDispatcher.dispatch()`. The Dispatcher authorizes each task before
publishing execution lifecycle events or calling `agent.execute()`. Agents
declare allowed actions through manifests; unknown actions fail closed as `T4`.

**Consequences:**

- The Brain remains semantic and agent-neutral.
- Agent-specific permission checks are avoided.
- Built-in and future Agents use the same T0-T4 gate, audit log, scoped session,
  confirmation, kill switch, and lock mode semantics.
- T2/T3 confirmation still flows through the existing conversation confirmation
  system; the Permission Engine does not create a second user-dialog system.
- Advanced scope validation, durable audit storage, rollback, and in-flight
  cancellation remain future hardening work.

**Related files:**

- `permissions/`
- `brain/dispatcher.py`
- `brain/planner.py`
- `core/events.py`
- `docs/permission_engine.md`
- `tests/test_permission_engine.py`

### DEC-0015: Treat Claude Sprint 2 Findings As Ship Blockers

**Date:** 2026-07-24
**Status:** Accepted

**Context:** Claude reviewed the Sprint 2 safety design and identified
ship-blocking risks around WebView bridge authentication, kill switch process
isolation, TOCTOU scope validation, confirmation binding, registry overwrite,
audit tamper evidence, routing order, and prompt injection into routing.

**Decision:** Track the findings as required safety gates on
`feature/NELA-safety-spine-routing`. Additive code may land only when it keeps
the Brain agent-neutral and prevents unrestricted Coding, Cyber, Browser, or
Terminal capabilities from becoming active.

**Consequences:**

- Future WebView bridge code must use restricted local transport and per-launch
  authentication.
- Blocking/high-risk Agents must run behind a subprocess boundary before they
  can claim forced termination semantics.
- T2/T3 confirmations must be bound to exact action tuples.
- Audit records must be tamper-evident.
- Agent/capability registration must not silently overwrite existing entries.
- Routing must authorize candidate capabilities before final Agent selection.

**Related files:**

- `docs/sprint2_claude_findings_status.md`
- `docs/agent_registry.md`
- `docs/audit_and_recovery.md`
- `docs/capability_routing.md`
- `docs/process_isolation.md`
- `docs/secure_ui_bridge.md`
- `ui/secure_bridge.py`
- `agents/process_isolation.py`
- `permissions/audit.py`
- `permissions/confirmation.py`
- `permissions/scope.py`
- `brain/dispatcher.py`

### DEC-0016: Runtime Language Learning And Defensive Cyber Routing

**Date:** 2026-07-25
**Status:** Accepted

**Context:** NELA needs to start learning user-provided words, short phrases,
and Q&A responses while also exposing the already-built defensive security
Agents through the Brain. This must not hardcode personality text in Brain code
or enable unrestricted cyber actions.

**Decision:** Store user-taught trigger/response pairs as local runtime data in
`data/language/learned_responses.json`, written only through `LearningAgent`
behind the Dispatcher and Permission Engine. `KnowledgeEngine` may read the same
store and answer matching future turns through the semantic `qa.learned`
category. Cyber/security conversation routing is limited to defensive,
read-only or local-lab-safe actions: security capability explanation, passive
security review, threat-model scaffolding, lab status, local lab target
registration, and local-only fuzz planning.

**Consequences:**

- Claude-authored language packs remain the source for NELA's authored tone.
- User-taught responses are local, reviewable data rather than code changes.
- Learning writes are `T1`; passive security reads/plans are `T0`; lab target
  registration is `T1`.
- Active cyber actions still require authorization, scoped sessions,
  confirmation, audit records, process isolation, and the kill switch.
- No external targeting, exploitation, credential theft, persistence, evasion,
  malware, or exfiltration path is introduced.

**Related files:**

- `language/learning_store.py`
- `agents/learning/agent.py`
- `brain/qa.py`
- `brain/intent_router.py`
- `brain/planner.py`
- `docs/language_system.md`
- `docs/cyber_lab.md`
- `tests/test_conversation_qa.py`
