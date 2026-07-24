# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation, Integration Sprint 1, the Claude language/personality drop, the multi-agent architecture specifications, Sprint 2 Permission Engine implementation, and Claude Sprint 2 safety findings are being consolidated on `feature/NELA-safety-spine-routing`.

The Brain now supports text and voice-transcript input, structured intent recognition, decision making, planning, context tracking, short-term and long-term memory orchestration, and Agent dispatch through a shared event bus.

The Brain does not perform external actions directly. It delegates Tasks to registered Agents. Most external integrations remain safe placeholders. Desktop Agent V1 is the first real execution Agent and is limited to safe macOS application lifecycle management.

The following branches are included in `develop`:

- `feature/NELA-0002-confirmation-deadlock`
- `feature/NELA-0005-desktop-agent-v1`
- `feature/NELA-0006-ui-foundation`
- `feature/NELA-0007-ai-inbox`
- `feature/NELA-0011-visual-identity`
- `feature/NELA-0012-claude-review-fixes`
- `feature/NELA-language-voice-foundation`

Integration Sprint 1 created backup branch `backup/develop-before-integration-20260723-050921`, verified branch inclusion, added Hebrew smoke-intent compatibility, mapped Voice speech events into UI Eye states, and generated `docs/integration_sprint_1_merge_report.md`.

Repository stabilization documented untracked duplicate-suffix files in `docs/untracked_duplicate_files_report.md`. The duplicate files were inspected only and left untouched. `develop` and backup branch `backup/develop-before-integration-20260723-050921` were pushed to GitHub through the configured SSH remote; `main` was not changed during this stabilization task.

On 2026-07-24, `nela-language-drop-final.zip` was integrated into the language foundation. Claude's Hebrew personality documents, tone rules, conversation rules, pack schema, 117-phrase Hebrew pack, and 3 personality presets are now stored in the repository. The Language Engine supports Claude compatibility metadata while keeping Brain code semantic and phrase-free.

On 2026-07-24, Claude's `nela-architecture.zip` deliverable was staged as repository documentation on `feature/NELA-architecture-specs`. This is specification-only work: no Coding Agent, Cyber Agent, Research Agent, advanced orchestration runtime, or new side-effecting capability was implemented.

On 2026-07-24, Sprint 2 implemented and hardened the Permission Engine on `feature/NELA-safety-spine-routing`. This is infrastructure-only work: no unrestricted Coding Agent, Cyber Agent, Browser/Vision/Cyber feature expansion, or UI redesign was added.

The consolidation includes:

- Confirmation answer routing before intent classification, including affirmative replies, negative replies, unclear reply handling, and TTL expiry.
- Safe mock Agents for MVP dispatch.
- Dispatcher timeout/retry hardening for the current synchronous execution model.
- Deterministic keyword/phrase intent matching, avoiding substring false positives.
- Desktop Agent V1 for known macOS app lookup, running detection, launch/focus, foreground switching, graceful close, structured results, and health reporting.
- A modular UI foundation with state management, event bridge, router, theme tokens, animation hooks, and a temporary Tkinter shell.
- `docs/ai_inbox.md` and a GitHub Issue template for AI collaboration tasks.
- Claude's Living Eye visual identity artifacts under `design/` and the authoritative design-system document under `docs/design_system.md`.
- Claude review fixes for Desktop timeout handling, Dispatcher exception isolation, Desktop `wait_until_ready`, `CloseApplication` confirmation, WebView-compatible UI host decision, and Inbox/Handoff cleanup.
- A standalone Hebrew Language Engine and Voice Agent Foundation. Phrase selection lives in `language/`, final response rendering lives in `core/response.py`, and speech playback lives in the `voice/` provider layer plus `agents/voice/agent.py`.
- Claude language system integration: `pack/categories/variants` pack shape, `speech_text`, `eye_state`, `gender_tier`, `min_stage`, session use counts, gender tag rendering, and personality `preset/params/pack_overrides` compatibility.
- Multi-agent architecture specifications: shared T0-T4 permission model, runtime lifecycle architecture, Coding Agent spec, defensive Cyber Agent spec, multi-agent orchestration spec, and AI system roadmap.
- Sprint 2 Permission Engine: T0-T4 tiers, Capability Registry, Agent manifests, authentication checks, confirmation gate, scoped sessions, in-memory audit log, kill switch, lock mode, permission events, UI state mapping for permission events, and Dispatcher integration before `agent.execute()`.
- Claude Sprint 2 findings: secure local bridge foundation, subprocess isolation foundation, symlink-aware scope validation, exact confirmation binding, insert-only Agent registration, tamper-evident audit hash chain, and authorization-before-final-routing foundation.

Claude collaboration is repository-based only. There is no direct Claude connection. Use direct GitHub `blob/` links, `docs/ai_inbox.md`, or regenerate a review bundle with `python3 -m scripts.export_claude_review_bundle`.

GitHub is the shared collaboration layer. The public repository is `https://github.com/edentiram72-1/nela`.

Claude also referenced a Memory subsystem deliverable, `nela-memory-subsystem.zip`, but that archive was not present in `/Users/edentiram/Downloads`, `/Users/edentiram/Downloads/files`, or the current attachment directory. Memory subsystem integration is blocked until that zip is provided.

## Current Milestone

**Sprint 2: Safety Spine + Intelligent Routing**

## Active Branch

`feature/NELA-safety-spine-routing`

## Recently Modified Files

- `README.md`
- `README.he.md`
- `.gitignore`
- `.env.example`
- `LICENSE`
- `core/app.py`
- `core/config.py`
- `core/events.py`
- `core/logger.py`
- `core/response.py`
- `core/startup.py`
- `language/*`
- `language/hebrew/*`
- `language/personality/*`
- `brain/conversation.py`
- `brain/context.py`
- `brain/decision.py`
- `brain/dispatcher.py`
- `brain/intent_router.py`
- `brain/applications.py`
- `brain/memory_manager.py`
- `brain/planner.py`
- `permissions/__init__.py`
- `permissions/audit.py`
- `permissions/engine.py`
- `permissions/models.py`
- `permissions/registry.py`
- `permissions/confirmation.py`
- `permissions/scope.py`
- `docs/permission_engine.md`
- `docs/agent_registry.md`
- `docs/audit_and_recovery.md`
- `docs/capability_routing.md`
- `docs/process_isolation.md`
- `docs/secure_ui_bridge.md`
- `docs/sprint2_claude_findings_status.md`
- `brain/reasoning.py`
- `agents/base.py`
- `agents/mock.py`
- `agents/registry.py`
- `agents/process_isolation.py`
- `agents/automation/agent.py`
- `agents/browser/agent.py`
- `agents/calendar/agent.py`
- `agents/claude/agent.py`
- `agents/codex/agent.py`
- `agents/desktop/agent.py`
- `agents/files/agent.py`
- `agents/github/agent.py`
- `agents/gmail/agent.py`
- `agents/memory/agent.py`
- `agents/memory/__init__.py`
- `agents/spotify/agent.py`
- `agents/terminal/agent.py`
- `agents/voice/agent.py`
- `agents/voice/__init__.py`
- `agents/vision/agent.py`
- `scripts/export_claude_review_bundle.py`
- `scripts/validate_language_packs.py`
- `docs/ai_handoff.md`
- `docs/ai_inbox.md`
- `docs/language_system.md`
- `docs/voice_architecture.md`
- `docs/integration_sprint_1_merge_report.md`
- `docs/untracked_duplicate_files_report.md`
- `docs/personality_bible.md`
- `docs/hebrew_language_guide.md`
- `docs/tone_of_voice.md`
- `docs/conversation_rules.md`
- `docs/language_compat_report.md`
- `docs/claude_handoff_2026-07-24.md`
- `docs/releases/v0.1-alpha.md`
- `docs/permission_model.md`
- `docs/nela_runtime_architecture.md`
- `docs/coding_agent_spec.md`
- `docs/cyber_agent_spec.md`
- `docs/multi_agent_orchestration.md`
- `docs/ai_system_roadmap.md`
- `docs/design_system.md`
- `docs/claude_review_bundle.md` generated locally for Claude review; ignored by Git to reduce merge conflicts.
- `memory/short_term.py`
- `memory/long_term.py`
- `memory/vector_store.py`
- `memory/profile.py`
- `voice/*`
- `voice/providers/*`
- `vision/*`
- `docs/architecture.md`
- `docs/api.md`
- `docs/coding_rules.md`
- `docs/claude_review_findings.md`
- `docs/decisions.md`
- `docs/memory_model.md`
- `docs/roadmap.md`
- `brain/README.md`
- `core/README.md`
- `agents/README.md`
- `memory/README.md`
- `voice/README.md`
- `vision/README.md`
- `tests/*`
- `tests/test_conversation_confirmations.py`
- `tests/test_desktop_agent.py`
- `tests/test_dispatcher.py`
- `tests/test_permission_engine.py`
- `tests/test_audit_log.py`
- `tests/test_process_isolation.py`
- `tests/test_secure_bridge.py`
- `tests/test_intent_recognition.py`
- `tests/test_planner.py`
- `ui/app.py`
- `ui/window.py`
- `ui/router.py`
- `ui/state.py`
- `ui/events.py`
- `ui/theme.py`
- `ui/animations.py`
- `ui/state.py`
- `ui/window.py`
- `ui/components/*`
- `ui/chat/*`
- `ui/sidebar/*`
- `ui/status/*`
- `ui/voice/*`
- `ui/eye/*`
- `ui/settings/*`
- `ui/assets/.gitkeep`
- `tests/test_ui_app.py`
- `tests/test_ui_router.py`
- `tests/test_ui_state.py`
- `tests/test_language_engine.py`
- `tests/test_voice_agent.py`
- `tests/test_language_voice_integration.py`
- `language/pack_schema.md`
- `language/pack_format.py`
- `tests/test_intent_recognition.py`
- `tests/test_ui_state.py`
- `.github/ISSUE_TEMPLATE/ai_collaboration_inbox.md`
- `design/nela_living_eye.html`
- `design/nela_app_icon.svg`
- `design/nela_menubar_icon.svg`

## Pending Tasks

- Create a draft PR from `develop` to `main` through GitHub web UI or authenticated `gh`.
- Do not merge further into `main` as part of Integration Sprint 1.
- Tag a stable release only after the user explicitly approves a release step.
- Provide `nela-memory-subsystem.zip` so a dedicated memory subsystem branch can be created and tested separately.
- Use `docs/ai_inbox.md` as the shared queue for Claude, Codex, and ChatGPT.
- Treat Phase A Safety Spine as the next implementation gate before any advanced Agents.
- Continue `NELA-0004-task-idempotency` before enabling real side effects.
- Review and merge Sprint 2 Permission Engine before implementing Browser Agent, Terminal Agent, Files Agent, Coding Agent, Cyber Agent, or communication Agents with real side effects.
- Continue the remaining hardening around the Permission Engine: durable audit storage, richer scope validation, rollback handling, and in-flight cancellation.
- Continue `NELA-0007-event-bus-hardening` with subscriber isolation, bounded history, and trace/correlation conventions.
- Continue `NELA-0008-capability-registry` so Planner/Dispatcher can reason about Agent capabilities and availability.
- Continue `NELA-0009-plan-executor` before relying on parallel, conditional, cancellable, or async orchestration semantics.
- Add `NELA-0016-audit-log-and-kill-switch` and `NELA-0017-agent-runtime-lifecycle` from `docs/ai_inbox.md`.
- Convert accepted Claude review findings from `docs/claude_review_findings.md` into tracked GitHub issues or roadmap entries.
- Try interactive NELA sessions through `python3 -m core.app`.
- Try the desktop UI shell with `python3 -m ui.app` on a machine with a graphical session.
- Send consolidated `develop` or `main` direct blob links to Claude for release verification.
- Ask Claude to review `docs/claude_handoff_2026-07-24.md`, `docs/personality_bible.md`, `docs/hebrew_language_guide.md`, `docs/tone_of_voice.md`, `docs/conversation_rules.md`, `language/pack_schema.md`, and `language/hebrew/`.
- Choose and implement a WebView-compatible host for the Living Eye.
- Add a durable persistence backend for long-term memory.
- Add a real plugin loader for `plugins/`.
- Add true concurrent execution for `TaskMode.PARALLEL`.
- Add condition evaluation for `TaskMode.CONDITIONAL`.
- Ask Claude to replace or expand the seed Hebrew language pack and personality profiles. Codex should not invent NELA's final personality.

## Known Issues

- Desktop Agent V1 performs real macOS application lifecycle actions for supported applications only. Other Agents remain safe mock placeholders.
- Live validation opened/foregrounded Finder only. Do not live-test close commands on user applications unless the user explicitly approves the target app.
- UI foundation intentionally has no Claude visual design yet. Eye, theme, animation, and component APIs expose states and tokens so Claude assets can be dropped in later without changing Brain architecture.
- Living Eye artifacts are present, but the Tkinter shell still renders a placeholder Eye component. Embedding `design/nela_living_eye.html` into the live app needs a future UI host decision, such as WebView, Electron, or Tauri.
- `DEC-0007` accepts that the production visual shell should use a WebView-compatible host. Tkinter remains temporary infrastructure only.
- Memory subsystem integration is blocked because `nela-memory-subsystem.zip` was not provided with the current files.
- The AI Inbox is repository-based only. It does not connect directly to Claude, Codex, or ChatGPT.
- Intent recognition is deterministic and rule-based; no LLM or external NLP provider is connected.
- Event bus is synchronous and in-process only.
- Long-term memory is in-memory only and does not persist after restart.
- Task timeout metadata is handled per attempt, but synchronous Agent execution still cannot interrupt a blocking Agent while it is running.
- GitHub Pull Request creation through the Codex GitHub connector returned `403 Resource not accessible by integration`; use GitHub web UI or install/authenticate GitHub CLI if a PR must be opened from the local machine.
- `docs/claude_review_bundle.md` is generated from the current branch and should be regenerated after meaningful architecture or code changes.
- Claude review found several hardening gaps to address before real agents are trusted: task idempotency, event bus subscriber isolation, permission policy, capability registry clarity, and future confidence scoring for intent matching.
- `Remember` requests create a Plan targeting the registered mock `memory` Agent while durable memory also updates through `MemoryManager`; this dual path should be simplified before durable persistence work.
- README architecture diagrams do not yet show the Decision Engine and Dispatcher explicitly.
- Hebrew Language Engine and Voice Agent Foundation are still foundation-stage, but the Hebrew pack is now Claude's authoritative content drop rather than the earlier Codex seed pack.
- Voice defaults to silent mode, so response-to-voice delegation is exercised without audio playback unless explicitly enabled.
- The macOS `say` provider is the local MVP provider and treats provider submission as completion. It does not provide portable pause/resume.
- Integration Sprint 1 found and fixed two compatibility gaps: Hebrew open-app smoke intent recognition, and Voice task completion overriding `SpeechCompleted -> IDLE`.
- GitHub CLI (`gh`) is not installed in the current shell, and the Codex GitHub connector returned `403 Resource not accessible by integration` when creating a draft PR. Draft Pull Request creation must happen through GitHub web UI or after installing/authenticating `gh`.
- 94 untracked duplicate-suffix files exist locally and are documented in `docs/untracked_duplicate_files_report.md`; they were not staged or modified.
- The current Language Engine supports Claude metadata needed for loading and rendering, but the full anti-repetition, humor budget, time-of-day, relationship-stage memory wiring, and phrase event observability from `language/pack_schema.md` are not fully implemented yet.
- `docs/permission_model.md`, `docs/nela_runtime_architecture.md`, `docs/coding_agent_spec.md`, `docs/cyber_agent_spec.md`, `docs/multi_agent_orchestration.md`, and `docs/ai_system_roadmap.md` are specifications only. Their runtime systems are not implemented yet.
- Cybersecurity capabilities must remain blocked until the permission model, capability registry, audit logging, kill switch, and isolated lab architecture exist.
- Sprint 2 Permission Engine exists and Claude Sprint 2 blocking findings have foundation implementations, but Cybersecurity capabilities must still remain blocked until isolated lab architecture, durable audit storage, task idempotency, and production event-bus hardening are complete.
- Terminal and Coding manifests declare future capabilities for review only. Side-effecting terminal execution and coding write/commit capabilities are disabled.

## Validation

Latest Sprint 2 validation on `feature/NELA-safety-spine-routing`:

```text
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
python3 -m core.app --once "נלה, תפתחי את Spotify" --no-dispatch
```

Result: 99 tests passed; language pack validation passed; headless UI bootstrap succeeded; Hebrew no-dispatch smoke produced `Intent: OpenApplication` and one semantic launch task.

Additional syntax validation:

```text
python3 -m compileall permissions brain/dispatcher.py brain/planner.py core/events.py ui/events.py tests/test_permission_engine.py tests/test_dispatcher.py tests/test_conversation_confirmations.py
```

Result: completed successfully.

Latest consolidation validation on `develop`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
python3 -m scripts.validate_language_packs
python3 -m core.app --once "נלה, תפתחי את Spotify"
```

Result: 66 tests passed; headless UI bootstrap succeeded; Hebrew language pack validation passed. This branch is specification-only and does not intentionally change runtime behavior.

Latest Integration Sprint 1 smoke:

```text
Input: נלה, תפתחי את Spotify
intent=OpenApplication
application=Spotify
plan_tasks=1
response=הפעלתי את Spotify.
ui_displayed=True
voice_spoken=True
eye_log=idle>listening>thinking>executing>success>executing>speaking>idle
eye_final=idle
```

Integration validation history:

- Baseline `origin/develop` after PR #1: 18 tests passed.
- After merging `feature/NELA-0002-confirmation-deadlock`: 27 tests passed.
- After merging `feature/NELA-0005-desktop-agent-v1`: 38 tests passed.
- After merging `feature/NELA-0006-ui-foundation`: 44 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-0007-ai-inbox`: 44 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-0011-visual-identity`: 45 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-0012-claude-review-fixes`: 49 tests passed; headless UI bootstrap succeeded.
- After merging `feature/NELA-language-voice-foundation`: 63 tests passed; headless UI bootstrap succeeded; language pack validation passed.

Latest validation for `NELA-0002-confirmation-deadlock`:

```text
python3 -m unittest discover -s tests
```

Result: 27 tests passed.

Latest validation for `NELA-0005-desktop-agent-v1`:

```text
python3 -m unittest discover -s tests
```

Result: 38 tests passed.

Latest validation for `NELA-0006-ui-foundation`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result: 44 tests passed; headless UI bootstrap succeeded.

Latest validation for `NELA-0011-visual-identity`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result: 45 tests passed; headless UI bootstrap succeeded; Claude Living Eye artifacts were copied into `design/`, `docs/design_system.md` was added, and UI event-state mapping tests passed.

Latest validation for `NELA-0012-claude-review-fixes`:

```text
python3 -m unittest discover -s tests
python3 -m core.app --once "close Finder" --no-dispatch
python3 -m ui.app --headless-smoke
```

Result: 49 tests passed; `close Finder` now asks for confirmation before planning; UI headless bootstrap succeeded.

Latest validation for `NELA-language-voice-foundation`:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m core.app --once "Open Spotify and play my Night playlist" --no-dispatch
python3 -m ui.app --headless-smoke
```

Result: language pack valid; 63 tests passed; CLI printed a Hebrew `NELA Response`; headless UI bootstrap succeeded.

Window launch smoke:

```text
Instantiate NelaWindow, schedule root.destroy(), run Tk mainloop.
```

Result: Tkinter UI window launched and closed successfully.

Claude bundle generation:

```text
python3 -m scripts.export_claude_review_bundle --output docs/claude_review_bundle.md --focus "Review NELA OS Phase 1 Brain foundation for architecture, event model, memory, agent lifecycle, plugin readiness, security, permissions, error recovery, and long-term maintainability."
```

Result: bundle generated successfully with 26 included files.

Application smoke test:

```text
python3 -m core.app
```

Result: runtime bootstrapped successfully.

CLI one-shot smoke test:

```text
python3 -m core.app --once "open Finder"
```

Result: Brain summary printed successfully, created one Desktop task, dispatched it to the real Desktop Agent, and macOS brought Finder to the foreground.

GitHub public access check:

```text
git ls-remote https://github.com/edentiram72-1/nela.git HEAD refs/heads/main refs/heads/develop refs/heads/feature/NELA-0001-foundation-architecture
```

Result: public HTTPS branch lookup succeeded.

## Suggested Next Task

Finish the develop consolidation handoff:

- Create a draft PR from `develop` to `main` through GitHub web UI or authenticated `gh`.
- Send Claude direct blob links for `docs/claude_handoff_2026-07-24.md`, `docs/ai_handoff.md`, `docs/personality_bible.md`, `docs/hebrew_language_guide.md`, `docs/tone_of_voice.md`, `docs/conversation_rules.md`, `language/pack_schema.md`, `language/hebrew/`, and `language/personality/`.

After release, continue in this order:

1. Memory subsystem integration after `nela-memory-subsystem.zip` is provided.
2. WebView-compatible Living Eye host.
3. Production voice provider behind the existing Voice Agent contract.
4. `NELA-0004-task-idempotency`.
5. Review and merge Sprint 2 Permission Engine.
6. `NELA-0007-event-bus-hardening`.
7. Expand Sprint 2 capability registry into plugin manifest loading.
8. Durable audit storage, richer scope validation, rollback handling, and runtime isolation before real advanced Agents.

## Notes For The Next AI Assistant

- Do not create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- For Claude review, share `docs/ai_inbox.md` direct blob links or regenerate `docs/claude_review_bundle.md` and paste/upload it to Claude.
- Read `docs/architecture.md`, `docs/api.md`, and `docs/coding_rules.md` before changing code.
- Keep the Brain agent-neutral.
- Keep Hebrew phrasing and personality rules out of Brain modules.
- Keep provider-specific voice code out of the Language Engine.
- Put execution logic inside Agents only.
- Register new Agents through `AgentDispatcher.register_agent()`.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
