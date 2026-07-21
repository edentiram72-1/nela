# NELA OS

NELA OS is a desktop-first AI operating system foundation inspired by the idea of a JARVIS-like intelligent assistant.

The project is designed to evolve into a modular assistant capable of voice conversation, memory, computer control, vision, automation, plugin support, multi-agent orchestration, and future mobile integration.

## Mission

Build a maintainable AI operating layer where one central Brain understands requests, reasons about them, creates plans, and delegates execution to independent Agents.

The Brain never executes actions directly. Agents do the work. Modules communicate through events instead of direct cross-module dependencies.

## Current Status

This repository contains the foundation architecture:

- Core runtime primitives.
- Central event bus.
- Brain, planner, reasoning, and intent routing skeletons.
- Memory module skeletons.
- Voice and vision interfaces.
- Independent agent contract and initial agent placeholders.
- GitHub collaboration templates.
- Documentation and AI handoff process.
- Basic unit tests using Python's built-in `unittest`.

No real desktop, voice, browser, Spotify, Gmail, or GitHub automation has been implemented yet.

## Architecture Flow

```text
Voice
  |
  v
Conversation
  |
  v
Brain
  |
  +--> Planner
  +--> Memory
  +--> Intent Router
  |
  v
Agents
  |
  v
Computer
```

## Repository Map

| Path | Purpose |
| --- | --- |
| `core/` | App startup, config, events, logging, and shared runtime primitives. |
| `brain/` | Conversation orchestration, reasoning, planning, and intent routing. |
| `voice/` | Wake word, microphone, speech-to-text, and text-to-speech interfaces. |
| `vision/` | Screen capture, screen reading, OCR, and UI detection interfaces. |
| `memory/` | Short-term memory, long-term memory, vector storage, and user profile. |
| `agents/` | Independent execution agents for desktop, terminal, browser, Spotify, files, calendar, Gmail, GitHub, Codex, automation, and vision. |
| `skills/` | Reusable capabilities that agents or the Brain may load later. |
| `plugins/` | Installable capability packages such as weather, YouTube, Slack, WhatsApp, Home Assistant, and iPhone support. |
| `docs/` | Architecture, roadmap, API notes, coding rules, memory model, and AI handoff. |
| `prompts/` | Role prompts for Codex, Claude, and ChatGPT. |
| `tests/` | Unit and integration tests. |
| `scripts/` | Developer utilities. |
| `config/` | Configuration defaults and templates. |
| `assets/` | Sounds, voices, and future media assets. |
| `logs/` | Runtime log output. Log files are ignored by Git. |

## Agent Contract

Every Agent exposes:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

The contract is defined in `agents/base.py`.

## Event Model

Agents and modules communicate through events. They should not call each other directly.

Example:

```text
Voice -> IntentRecognized -> Planner -> TaskCreated -> SpotifyAgent -> TaskCompleted
```

The event bus is defined in `core/events.py`.

## Run The Foundation

```bash
python -m core.app
```

## Run Tests

```bash
python -m unittest discover -s tests
```

## Git Strategy

- `main`: stable production-ready history.
- `develop`: integration branch for accepted work before release.
- `feature/*`: one feature per branch.
- `bugfix/*`: one bug fix per branch.
- `release/*`: release preparation.

## AI Collaboration

- ChatGPT: architecture, planning, reasoning, specifications, and major structural approvals.
- Codex: implementation, bug fixing, testing, and refactoring.
- Claude: architecture review, documentation review, UX review, risk analysis, and performance suggestions.

GitHub is the collaboration layer. Do not create direct communication channels between AI assistants.

## First Step For Any AI Assistant

1. Read `docs/ai_handoff.md`.
2. Read `docs/architecture.md`.
3. Check the active Git branch.
4. Confirm the current task and target module.
5. Update `docs/ai_handoff.md` before stopping work.

