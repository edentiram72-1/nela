# NELA OS

NELA OS is a modular AI operating layer designed for long-term collaboration between multiple assistants through GitHub.

The repository is intentionally structured so that Codex, Claude, ChatGPT, and future assistants can work independently while sharing the same source of truth.

## Collaboration Model

- GitHub is the collaboration layer.
- `docs/ai_handoff.md` is the primary handoff file between AI assistants.
- Each feature should be developed on its own branch.
- Every meaningful code or documentation change must update the handoff file.
- No direct communication channel with Claude or any other assistant is required.

## Repository Map

| Folder | Purpose |
| --- | --- |
| `core/` | Core runtime contracts, shared primitives, and system orchestration. |
| `agents/` | Independent AI agent modules and agent-specific adapters. |
| `memory/` | Memory storage interfaces, summaries, retrieval, and persistence logic. |
| `voice/` | Speech input, speech output, and audio interaction modules. |
| `vision/` | Image, screen, and visual understanding modules. |
| `planner/` | Planning, task decomposition, and execution strategy modules. |
| `automation/` | Scheduled jobs, triggers, monitors, and workflow automation. |
| `skills/` | Reusable capabilities that can be loaded by agents. |
| `terminal/` | Terminal execution, shell safety, and command tooling. |
| `browser/` | Browser interaction, navigation, and web task support. |
| `docs/` | Architecture, roadmap, API, handoff, decisions, and coding rules. |
| `prompts/` | Assistant role prompts for Codex, Claude, and ChatGPT. |
| `tests/` | Unit, integration, and module contract tests. |
| `scripts/` | Developer utilities, setup scripts, and maintenance commands. |
| `config/` | Environment-neutral configuration templates and defaults. |

## First Step For Any AI Assistant

1. Read `docs/ai_handoff.md`.
2. Read `docs/architecture.md`.
3. Check the active Git branch.
4. Confirm pending tasks before changing files.
5. Update `docs/ai_handoff.md` before handing off work.

