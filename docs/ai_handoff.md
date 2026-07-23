# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation, Integration Sprint 1, the Claude language/personality drop, and the first vertical-slice desktop demo are now in progress from the current `develop` baseline.

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

`feature/NELA-vertical-slice-demo` adds the first visible end-to-end demo. It starts with `python3 -m nela_runtime`, serves a local browser-hosted interface, embeds the original animated `design/nela_living_eye.html`, accepts Hebrew text, routes through the existing Brain and `UIRouter`, displays the Hebrew response, delegates the same response to `VoiceAgent`, and drives the Eye back to `IDLE`.

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
- Vertical-slice demo runtime: `nela_runtime/`, local browser WebView host, Hebrew chat flow, Living Eye state updates, and mocked end-to-end integration coverage.

Claude collaboration is repository-based only. There is no direct Claude connection. Use direct GitHub `blob/` links, `docs/ai_inbox.md`, or regenerate a review bundle with `python3 -m scripts.export_claude_review_bundle`.

GitHub is the shared collaboration layer. The public repository is `https://github.com/edentiram72-1/nela`.

Claude also referenced a Memory subsystem deliverable, `nela-memory-subsystem.zip`, but that archive was not present in `/Users/edentiram/Downloads`, `/Users/edentiram/Downloads/files`, or the current attachment directory. Memory subsystem integration is blocked until that zip is provided.

## Current Milestone

**Vertical Slice Demo: visible NELA flow with Living Eye, Hebrew Brain response, Desktop Agent, and Voice Agent**

## Active Branch

`feature/NELA-vertical-slice-demo`

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
- `brain/memory_manager.py`
- `brain/planner.py`
- `brain/reasoning.py`
- `agents/base.py`
- `agents/mock.py`
- `agents/registry.py`
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
- `docs/vertical_slice_demo.md`
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
- `tests/test_vertical_slice_demo.py`
- `language/pack_schema.md`
- `language/pack_format.py`
- `tests/test_intent_recognition.py`
- `tests/test_ui_state.py`
- `.github/ISSUE_TEMPLATE/ai_collaboration_inbox.md`
- `design/nela_living_eye.html`
- `design/nela_app_icon.svg`
- `design/nela_menubar_icon.svg`
- `nela_runtime/__init__.py`
- `nela_runtime/__main__.py`
- `nela_runtime/server.py`

## Pending Tasks

- Create a draft PR from `develop` to `main` through GitHub web UI or authenticated `gh`.
- Do not merge further into `main` as part of Integration Sprint 1.
- Tag a stable release only after the user explicitly approves a release step.
- Provide `nela-memory-subsystem.zip` so a dedicated memory subsystem branch can be created and tested separately.
- Use `docs/ai_inbox.md` as the shared queue for Claude, Codex, and ChatGPT.
- Continue `NELA-0004-task-idempotency` before enabling real side effects.
- Continue `NELA-0006-permission-policy` before implementing Browser Agent, Terminal Agent, Files Agent, or communication Agents with real side effects.
- Continue `NELA-0007-event-bus-hardening` with subscriber isolation, bounded history, and trace/correlation conventions.
- Continue `NELA-0008-capability-registry` so Planner/Dispatcher can reason about Agent capabilities and availability.
- Convert accepted Claude review findings from `docs/claude_review_findings.md` into tracked GitHub issues or roadmap entries.
- Try interactive NELA sessions through `python3 -m core.app`.
- Try the desktop UI shell with `python3 -m ui.app` on a machine with a graphical session.
- Send consolidated `develop` or `main` direct blob links to Claude for release verification.
- Ask Claude to review `docs/claude_handoff_2026-07-24.md`, `docs/personality_bible.md`, `docs/hebrew_language_guide.md`, `docs/tone_of_voice.md`, `docs/conversation_rules.md`, `language/pack_schema.md`, and `language/hebrew/`.
- Review `feature/NELA-vertical-slice-demo` and decide whether the local browser-hosted WebView demo should later move to Tauri, Electron, Python WebView, or another production shell.
- Add a durable persistence backend for long-term memory.
- Add a real plugin loader for `plugins/`.
- Add true concurrent execution for `TaskMode.PARALLEL`.
- Add condition evaluation for `TaskMode.CONDITIONAL`.
- Ask Claude to replace or expand the seed Hebrew language pack and personality profiles. Codex should not invent NELA's final personality.

## Known Issues

- Desktop Agent V1 performs real macOS application lifecycle actions for supported applications only. Other Agents remain safe mock placeholders.
- Live validation has opened/foregrounded Finder and Spotify only. Do not live-test close commands on user applications unless the user explicitly approves the target app.
- UI foundation intentionally has no Claude visual design yet. Eye, theme, animation, and component APIs expose states and tokens so Claude assets can be dropped in later without changing Brain architecture.
- Living Eye artifacts are rendered in the vertical-slice browser-hosted demo. The older Tkinter shell still renders a placeholder Eye component and remains temporary.
- `DEC-0007` accepts that the production visual shell should use a WebView-compatible host. Tkinter remains temporary infrastructure only.
- `DEC-0012` selects a local browser-hosted WebView host for the vertical slice demo only; the final production shell decision remains open.
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

## Validation

Latest consolidation validation on `develop`:

```text
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
python3 -m scripts.validate_language_packs
python3 -m core.app --once "נלה, תפתחי את Spotify"
python3 -m nela_runtime --headless-smoke
python3 -m unittest tests.test_vertical_slice_demo
```

Result: 68 tests passed; headless UI bootstrap succeeded; vertical-slice runtime bootstrap succeeded; Hebrew language pack validation passed; Hebrew Spotify CLI smoke returned a Claude-pack Hebrew NELA response and brought Spotify forward through the safe Desktop Agent.

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
5. `NELA-0006-permission-policy`.
6. `NELA-0007-event-bus-hardening`.
7. `NELA-0008-capability-registry`.

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
