# NELA OS Architecture

## Purpose

NELA OS is a modular AI operating layer. Its architecture is designed for multiple AI assistants to collaborate safely through GitHub while keeping every feature isolated, documented, and traceable.

The system should evolve through small, independent modules rather than large coupled rewrites.

## Architectural Principles

1. **GitHub is the source of truth.** All assistants coordinate through branches, commits, pull requests, issues, and the handoff document.
2. **Modules stay independent.** A feature should live in the most specific folder possible and expose a narrow interface.
3. **Documentation changes with behavior.** Any meaningful change must update relevant docs and `docs/ai_handoff.md`.
4. **Architecture is explicit.** Major structural changes require a decision entry in `docs/decisions.md`.
5. **Tests follow risk.** Add tests whenever practical, especially for shared contracts, data transformations, and automation.

## Top-Level Modules

### `core/`

Core runtime contracts, shared primitives, orchestration interfaces, and cross-module types. Code in this folder should be stable and reviewed carefully because changes may affect the entire system.

### `agents/`

Independent AI agent modules and agent-specific adapters. Each agent implementation should be isolated behind a clear interface so that one assistant's workflow does not force changes in another assistant's module.

### `memory/`

Memory storage, retrieval, summarization, indexing, and persistence. This folder should separate memory interfaces from storage backends so the project can change persistence strategies later.

### `voice/`

Speech input, speech output, transcription, voice synthesis, and audio-related interaction logic.

### `vision/`

Image understanding, screen analysis, OCR, and visual context processing.

### `planner/`

Planning, task decomposition, prioritization, scheduling decisions, and execution strategies.

### `automation/`

Scheduled jobs, event triggers, monitors, background workflows, and repeatable operational tasks.

### `skills/`

Reusable assistant capabilities. A skill should be self-contained and documented enough that any AI can understand when to use it.

### `terminal/`

Terminal command execution, shell integration, command safety, and local development tooling.

### `browser/`

Browser control, page inspection, navigation, web task support, and browser automation helpers.

### `config/`

Configuration templates and defaults. Secrets must not be committed.

## Dependency Direction

Recommended dependency direction:

```text
apps/features -> agents/planner/automation -> core
voice/vision/browser/terminal -> core
memory -> core
tests -> all modules
```

Avoid circular dependencies. Shared behavior belongs in `core/`; module-specific behavior should remain inside its module.

## Change Workflow

1. Create one branch per feature or fix.
2. Read `docs/ai_handoff.md` before starting.
3. Keep changes scoped to the relevant module.
4. Update documentation and handoff notes.
5. Add or update tests when practical.
6. Commit small, reviewable changes.
7. Open a pull request for review.

## Architecture Change Policy

Do not change the top-level architecture casually. Any major change must:

- Explain the reason for the change.
- Describe affected modules.
- Record the decision in `docs/decisions.md`.
- Update `docs/architecture.md`.
- Update `docs/ai_handoff.md`.

