# NELA OS Architecture

## Purpose

NELA OS is a desktop-first AI operating system foundation. It is designed to grow into an intelligent assistant that can converse by voice, remember context, understand the screen, control applications, automate workflows, and load new capabilities as plugins.

The system is built around one central Brain. The Brain understands, reasons, plans, and delegates. It does not execute actions directly.

## Core Architecture

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

## Principles

1. **The Brain delegates.** It never performs desktop, browser, file, or service actions directly.
2. **Agents execute.** Every capability is an independent Agent with the same lifecycle contract.
3. **Events connect modules.** Modules communicate through events, not direct dependencies.
4. **Memory is explicit.** Short-term, long-term, vector, and profile memory are separate concerns.
5. **Plugins extend capability.** New capabilities should be installable as plugins.
6. **Documentation follows behavior.** Significant changes update docs and `docs/ai_handoff.md`.
7. **GitHub is the collaboration layer.** AI assistants coordinate through branches, commits, pull requests, issues, and the handoff file.

## Project Structure

```text
NELA/
  README.md
  LICENSE
  .env.example
  .gitignore

  docs/
    architecture.md
    roadmap.md
    ai_handoff.md
    coding_rules.md
    api.md
    memory_model.md

  core/
    app.py
    config.py
    events.py
    logger.py
    startup.py

  brain/
    planner.py
    reasoning.py
    conversation.py
    intent_router.py

  voice/
    microphone.py
    speech_to_text.py
    text_to_speech.py
    wake_word.py

  vision/
    screen_capture.py
    screen_reader.py
    ui_detector.py

  memory/
    short_term.py
    long_term.py
    vector_store.py
    profile.py

  agents/
    terminal/
    browser/
    spotify/
    files/
    calendar/
    gmail/
    github/
    codex/
    automation/
    vision/
    desktop/

  skills/
  plugins/
  tests/
  scripts/
  config/
  assets/
    sounds/
    voices/
  logs/
  prompts/
```

## Core Components

### Brain

Responsible for:

- Understanding user intent.
- Reasoning about the request.
- Planning task execution.
- Delegating work to Agents.
- Emitting events that describe decisions and tasks.

Current files:

- `brain/conversation.py`
- `brain/intent_router.py`
- `brain/reasoning.py`
- `brain/planner.py`

### Planner

Breaks every request into executable tasks.

Example:

```text
User: "Open Spotify and play relaxing music."

Planner:
1. Open Spotify
2. Wait until Spotify is ready
3. Search for a relaxing music playlist
4. Start playback
```

### Memory

Stores:

- User profile.
- Preferences.
- Conversations.
- Projects.
- Long-term memories.
- Session memories.

See `docs/memory_model.md`.

### Voice

Responsible for:

- Wake word detection.
- Speech recognition.
- Speech synthesis.
- Voice input and output boundaries.

### Vision

Responsible for:

- Reading the screen.
- Understanding UI state.
- OCR.
- Detecting buttons, inputs, and other UI elements.
- Helping agents navigate applications.

### Agent System

Every capability is an independent Agent.

Each Agent exposes:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

Agents currently exist as placeholders for:

- Terminal
- Browser
- Spotify
- Files
- Calendar
- Gmail
- GitHub
- Codex
- Automation
- Vision
- Desktop

### Events

Every Agent communicates only through events. Direct agent-to-agent dependencies are not allowed.

Example:

```text
Voice
  |
  v
IntentRecognized
  |
  v
Planner
  |
  v
TaskCreated
  |
  v
SpotifyAgent
  |
  v
TaskCompleted
```

Current event primitives are defined in `core/events.py`.

### Plugin System

Every new capability should be installable as a plugin when it is not part of the core assistant runtime.

Examples:

```text
plugins/
  weather/
  youtube/
  slack/
  whatsapp/
  homeassistant/
  iphone/
```

Plugin loading is not implemented yet. The current repository only reserves the structure.

## Logging

Centralized logging is configured in `core/logger.py`.

Runtime log targets:

- `logs/brain.log`
- `logs/voice.log`
- `logs/agents.log`
- `logs/errors.log`
- `logs/performance.log`

Log files are ignored by Git. `logs/.gitkeep` keeps the folder available.

## Dependency Direction

Recommended dependency direction:

```text
core <- brain <- voice/conversation entry points
core <- agents
core <- memory
core <- vision
tests -> all modules
```

Rules:

- `brain/` may create plans and events, but must not execute external actions.
- `agents/` may execute actions, but must not make architecture decisions.
- `memory/` should expose storage interfaces without owning conversation flow.
- `voice/` and `vision/` should expose inputs to the Brain or Agents without directly controlling unrelated modules.
- Shared runtime primitives belong in `core/`.

## Documentation Requirements

Every module should document:

- Purpose.
- Dependencies.
- Events.
- Public API.
- Examples.
- Known limitations.
- Future improvements.

## Architecture Change Policy

Major structural changes must:

- Explain the reason for the change.
- Describe affected modules.
- Record the decision in `docs/decisions.md`.
- Update `docs/architecture.md`.
- Update `docs/ai_handoff.md`.

