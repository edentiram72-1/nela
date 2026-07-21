# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation has been implemented on top of the initial collaboration skeleton.

The Brain now supports text and voice-transcript input, structured intent recognition, decision making, planning, context tracking, short-term and long-term memory orchestration, and Agent dispatch through a shared event bus.

The Brain does not perform external actions directly. It delegates Tasks to registered Agents. Current Agents are placeholders and expose the required lifecycle contract, but they do not yet control real applications or services.

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

## Validation

Last validation run:

```text
python3 -m unittest discover -s tests
```

Result: all tests passed.

Application smoke test:

```text
python3 -m core.app
```

Result: runtime bootstrapped successfully.

## Suggested Next Task

Create task `NELA-0002-first-real-agent` and implement one real Agent behind the existing Agent contract without changing Brain architecture.

Recommended first Agent: `desktop` or `terminal`.

## Notes For The Next AI Assistant

- Do not create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- Read `docs/architecture.md`, `docs/api.md`, and `docs/coding_rules.md` before changing code.
- Keep the Brain agent-neutral.
- Put execution logic inside Agents only.
- Register new Agents through `AgentDispatcher.register_agent()`.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
