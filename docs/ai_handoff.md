# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation has been implemented on top of the initial collaboration skeleton.

The Brain now supports text and voice-transcript input, structured intent recognition, decision making, planning, context tracking, short-term and long-term memory orchestration, and Agent dispatch through a shared event bus.

The Brain does not perform external actions directly. It delegates Tasks to registered Agents. Most Agents are safe mock placeholders. Desktop Agent V1 is now in progress as the first real execution Agent, limited to safe macOS application lifecycle management.

`NELA-0002-confirmation-deadlock` has been implemented on a dedicated branch. The Conversation Engine now routes pending confirmation answers before intent classification, supports affirmative and negative replies, re-asks once for unclear replies, cancels after repeated unclear replies, and expires stale confirmations after a configurable TTL.

The MVP Brain Agent layer now includes registered placeholder Agents for Desktop, Terminal, Browser, Voice, Vision, Memory, Spotify, and File System. Extra collaboration and integration placeholders remain registered for automation, calendar, Gmail, GitHub, Claude, and Codex.

`NELA-0003-dispatcher-timeout-retry-safety` has started. Dispatcher timing is now tracked per attempt, slow successful mock Agent results are not rewritten as timeout failures, failed attempts that exceed timeout metadata report timeout, and retry success is covered by unit tests.

Intent matching now checks full keywords and phrases instead of arbitrary substrings, preventing false positives such as matching `play` inside `display`.

Claude collaboration is now supported through a generated review bundle. There is no direct Claude connection. Use `docs/claude_review_bundle.md` or regenerate it with `python3 -m scripts.export_claude_review_bundle`.

NELA can now run from the command line. Use `python3 -m core.app` for an interactive text session, `python3 -m core.app --once "<request>"` for a one-shot Brain run with mock dispatch, or add `--no-dispatch` to inspect the plan without sending tasks to Agents.

The root README is now a full English project overview, and `README.he.md` provides a full Hebrew version. Both summarize the architecture, completed work, GitHub/Claude collaboration flow, current limitations, and next recommended tasks.

`NELA-0005-desktop-agent-v1` has started on branch `feature/NELA-0005-desktop-agent-v1`. The Desktop mock has been replaced with a macOS lifecycle Agent that supports known application lookup, running detection, launch/focus, foreground switching, graceful close, structured results, and health reporting. Unit tests use a fake command runner and do not open or close real applications.

Desktop lifecycle intents now route through the existing Brain flow without architecture changes. `OpenApplication`, `CloseApplication`, and `SwitchApplication` create Desktop Agent tasks through the Planner.

The root README now documents Desktop Agent V1, supported applications, safety limits, known limitations, and the current feature branch.

`NELA-0006-ui-foundation` has started on branch `feature/NELA-0006-ui-foundation`. A modular desktop UI foundation now exists under `ui/` to host Claude's future visual design without redesigning the interface. It includes UI state management, theme tokens, animation hooks, Brain event integration, a router from text input to the existing Brain, a Tkinter window shell, chat/status/sidebar/voice/eye/settings component placeholders, and tests for state, routing, and headless app bootstrap.

GitHub is now the shared collaboration layer. The public repository is `https://github.com/edentiram72-1/nela`, and this feature branch has been pushed for review.

Claude reviewed the Phase 1 Brain foundation from the review bundle and identified the next architecture-hardening work. The findings are recorded in `docs/claude_review_findings.md`. The highest-priority issue was a deterministic confirmation deadlock where pending confirmations were not resolved before new intent classification, causing follow-up input to remain stuck in `WAIT`.

## Current Milestone

**Phase 1: Build The Brain**

## Active Branch

`feature/NELA-0006-ui-foundation`

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
- `core/startup.py`
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
- `docs/ai_handoff.md`
- `docs/claude_review_bundle.md` generated locally for Claude review; ignored by Git to reduce merge conflicts.
- `memory/short_term.py`
- `memory/long_term.py`
- `memory/vector_store.py`
- `memory/profile.py`
- `voice/*`
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

## Pending Tasks

- Open or finalize a GitHub Pull Request from `feature/NELA-0002-confirmation-deadlock` into `feature/NELA-0001-foundation-architecture` or `develop`.
- Finish `NELA-0006-ui-foundation` documentation, final validation, and GitHub push.
- Continue `NELA-0003-dispatcher-timeout-retry-safety` with idempotency metadata before enabling real side effects.
- Convert accepted Claude review findings from `docs/claude_review_findings.md` into tracked GitHub issues or roadmap entries.
- Try interactive NELA sessions through `python3 -m core.app`.
- Try the desktop UI shell with `python3 -m ui.app` on a machine with a graphical session.
- Send `NELA-0006-ui-foundation` to Claude for UI infrastructure review before Claude supplies visual assets.
- Add a durable persistence backend for long-term memory.
- Add a real plugin loader for `plugins/`.
- Add true concurrent execution for `TaskMode.PARALLEL`.
- Add condition evaluation for `TaskMode.CONDITIONAL`.
- Add a user confirmation workflow for sensitive tasks.

## Known Issues

- Desktop Agent V1 performs real macOS application lifecycle actions for supported applications only. Other Agents remain safe mock placeholders.
- Live validation opened/foregrounded Finder only. Do not live-test close commands on user applications unless the user explicitly approves the target app.
- UI foundation intentionally has no Claude visual design yet. Eye, theme, animation, and component APIs expose states and tokens so Claude assets can be dropped in later without changing Brain architecture.
- Intent recognition is deterministic and rule-based; no LLM or external NLP provider is connected.
- Event bus is synchronous and in-process only.
- Long-term memory is in-memory only and does not persist after restart.
- Task timeout metadata is handled per attempt, but synchronous Agent execution still cannot interrupt a blocking Agent while it is running.
- GitHub Pull Request creation through the Codex GitHub connector returned `403 Resource not accessible by integration`; use GitHub web UI or install/authenticate GitHub CLI if a PR must be opened from the local machine.
- `docs/claude_review_bundle.md` is generated from the current branch and should be regenerated after meaningful architecture or code changes.
- Claude review found several hardening gaps to address before real agents are trusted: dispatcher timeout/retry semantics, task idempotency, event bus subscriber isolation, intent matching precision, permission policy, and capability registry clarity.
- `Remember` requests create a Plan targeting the registered mock `memory` Agent while durable memory also updates through `MemoryManager`; this dual path should be simplified before durable persistence work.
- README architecture diagrams do not yet show the Decision Engine and Dispatcher explicitly.

## Validation

Last validation run:

```text
python3 -m unittest discover -s tests
```

Result: all tests passed.

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

Send UI Foundation to Claude for infrastructure review. Claude should review the state contracts, Eye states, theme token system, animation hooks, component boundaries, and whether the structure is ready for Claude's brand identity, Eye SVG, UI/UX, and design system.

Scope:

- Keep visual design out of Codex-owned code.
- Confirm Claude can replace placeholder components without Brain changes.
- Confirm the UI event bridge maps Brain events to the expected Eye and status states.

After UI review, continue permission and idempotency hardening before implementing Browser Agent, Terminal Agent, or Files Agent.

## Notes For The Next AI Assistant

- Do not create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- For Claude review, share `https://github.com/edentiram72-1/nela/tree/feature/NELA-0006-ui-foundation` and direct blob links, or regenerate `docs/claude_review_bundle.md` and paste/upload it to Claude.
- Read `docs/architecture.md`, `docs/api.md`, and `docs/coding_rules.md` before changing code.
- Keep the Brain agent-neutral.
- Put execution logic inside Agents only.
- Register new Agents through `AgentDispatcher.register_agent()`.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
