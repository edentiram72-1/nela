# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

Phase 1 Brain foundation has been implemented on top of the initial collaboration skeleton.

The Brain now supports text and voice-transcript input, structured intent recognition, decision making, planning, context tracking, short-term and long-term memory orchestration, and Agent dispatch through a shared event bus.

The Brain does not perform external actions directly. It delegates Tasks to registered Agents. Current Agents are placeholders and expose the required lifecycle contract, but they do not yet control real applications or services.

Claude collaboration is now supported through a generated review bundle. There is no direct Claude connection. Use `docs/claude_review_bundle.md` or regenerate it with `python3 -m scripts.export_claude_review_bundle`.

NELA can now run from the command line. Use `python3 -m core.app` for an interactive text session or `python3 -m core.app --once "<request>" --no-dispatch` for a one-shot Brain summary.

GitHub is now the shared collaboration layer. The public repository is `https://github.com/edentiram72-1/nela`, and this feature branch has been pushed for review.

Claude reviewed the Phase 1 Brain foundation from the review bundle and identified the next architecture-hardening work. The highest-priority issue is a confirmation deadlock where pending confirmations are not resolved before new intent classification, causing follow-up input to remain stuck in `WAIT`.

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

- Open or finalize a GitHub Pull Request from `feature/NELA-0001-foundation-architecture` into `develop`. GitHub public access is working, but the browser PR form intermittently failed to render the full comparison.
- Start `NELA-0002-confirmation-deadlock` and fix the pending-confirmation flow before adding real external Agents.
- Convert accepted Claude review findings into tracked issues or roadmap entries.
- Try interactive NELA sessions through `python3 -m core.app`.
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
- GitHub Pull Request creation through the Codex GitHub connector returned `403 Resource not accessible by integration`; use GitHub web UI or install/authenticate GitHub CLI if a PR must be opened from the local machine.
- `docs/claude_review_bundle.md` is generated from the current branch and should be regenerated after meaningful architecture or code changes.
- Claude review found several hardening gaps to address before real agents are trusted: dispatcher timeout/retry semantics, task idempotency, event bus subscriber isolation, intent matching precision, permission policy, and capability registry clarity.

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

GitHub public access check:

```text
git ls-remote https://github.com/edentiram72-1/nela.git HEAD refs/heads/main refs/heads/develop refs/heads/feature/NELA-0001-foundation-architecture
```

Result: public HTTPS branch lookup succeeded.

## Suggested Next Task

Create task `NELA-0002-confirmation-deadlock` and harden the Brain confirmation workflow before implementing real external Agents.

Scope:

- Resolve pending confirmations before classifying a follow-up message as a new intent.
- Add confirmation expiry or cancellation semantics.
- Add tests for approval, rejection, unclear reply, and repeated follow-up behavior.
- Keep all action execution delegated through Agents.

After `NELA-0002`, continue with dispatcher timeout/retry/idempotency hardening, then implement the first real Agent.

## Notes For The Next AI Assistant

- Do not create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- For Claude review, share `https://github.com/edentiram72-1/nela/tree/feature/NELA-0001-foundation-architecture` or regenerate `docs/claude_review_bundle.md` and paste/upload it to Claude.
- Read `docs/architecture.md`, `docs/api.md`, and `docs/coding_rules.md` before changing code.
- Keep the Brain agent-neutral.
- Put execution logic inside Agents only.
- Register new Agents through `AgentDispatcher.register_agent()`.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
