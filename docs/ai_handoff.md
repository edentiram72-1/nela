# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation has been implemented on top of the initial collaboration skeleton.

The Brain now supports text and voice-transcript input, structured intent recognition, decision making, planning, context tracking, short-term and long-term memory orchestration, and Agent dispatch through a shared event bus.

The Brain does not perform external actions directly. It delegates Tasks to registered Agents. Current Agents are placeholders and expose the required lifecycle contract, but they do not yet control real applications or services.

Claude collaboration is now supported through a generated review bundle. There is no direct Claude connection. Use `docs/claude_review_bundle.md` or regenerate it with `python3 -m scripts.export_claude_review_bundle`.

NELA can now run from the command line. Use `python3 -m core.app` for an interactive text session or `python3 -m core.app --once "<request>" --no-dispatch` for a one-shot Brain summary.

## Current Milestone

**Phase 1: Build The Brain**

## Active Branch

`feature/NELA-0001-foundation-architecture`

## Recently Modified Files

- `README.md`
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
- `agents/registry.py`
- `agents/claude/agent.py`
- `scripts/export_claude_review_bundle.py`
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

## Pending Tasks

- Review whether this branch should be merged into `develop` before `main`.
- Paste or upload `docs/claude_review_bundle.md` into Claude and capture review findings.
- Try interactive NELA sessions through `python3 -m core.app`.
- Create GitHub remote and push branches when the destination repository is known.
- Implement the first real Agent, preferably `desktop`, `terminal`, `browser`, or `files`.
- Add a durable persistence backend for long-term memory.
- Add a real plugin loader for `plugins/`.
- Add true concurrent execution for `TaskMode.PARALLEL`.
- Add condition evaluation for `TaskMode.CONDITIONAL`.
- Add a user confirmation workflow for sensitive tasks.

## Known Issues

- Agents are placeholders and intentionally return "not implemented" for real actions.
- Intent recognition is deterministic and rule-based; no LLM or external NLP provider is connected.
- Event bus is synchronous and in-process only.
- Long-term memory is in-memory only and does not persist after restart.
- Task timeout metadata exists, but synchronous Agent execution cannot interrupt a blocking Agent yet.
- No remote GitHub repository is configured locally.
- `docs/claude_review_bundle.md` is generated from the current branch and should be regenerated after meaningful architecture or code changes.

## Validation

Last validation run:

```text
python3 -m unittest discover -s tests
```

Result: all tests passed.

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
python3 -m core.app --once "Open Spotify and play my Night playlist" --no-dispatch
```

Result: Brain summary printed successfully.

## Suggested Next Task

Create task `NELA-0002-first-real-agent` and implement one real Agent behind the existing Agent contract without changing Brain architecture.

Recommended first Agent: `desktop` or `terminal`.

## Notes For The Next AI Assistant

- Do not create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- For Claude review, regenerate `docs/claude_review_bundle.md` and paste/upload it to Claude.
- Read `docs/architecture.md`, `docs/api.md`, and `docs/coding_rules.md` before changing code.
- Keep the Brain agent-neutral.
- Put execution logic inside Agents only.
- Register new Agents through `AgentDispatcher.register_agent()`.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
