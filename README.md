# NELA OS

English | [עברית](README.he.md)

NELA OS is a desktop-first AI operating system foundation inspired by the idea of a JARVIS-like intelligent assistant.

The project is being built as a modular, event-driven assistant that can grow into voice conversation, memory, computer control, screen understanding, automation, plugin support, multi-agent orchestration, and future mobile integration.

## Mission

Build a maintainable AI operating layer where one central Brain understands requests, reasons about them, creates plans, remembers context, and delegates execution to independent Agents.

The Brain never executes external actions directly. Agents do the work. Modules communicate through events instead of direct cross-module dependencies.

## Current Status

NELA OS is currently moving from **Phase 1: Build The Brain** into **Phase 2: Desktop UI Foundation**.

The repository now contains a working foundation that can:

- Start from the command line.
- Accept text or voice-transcript input.
- Classify user intent into structured data.
- Decide whether to ask, wait, remember, delegate, or reject.
- Create executable task plans.
- Track conversation context and running tasks.
- Manage short-term and long-term memory layers.
- Dispatch tasks to registered Agents through a shared contract.
- Publish lifecycle events through an in-process Event Bus.
- Use safe mock Agents for MVP validation while Desktop Agent V1 begins real macOS application lifecycle control.
- Launch a modular desktop UI shell that connects user text input to the existing Brain.
- Export Claude review bundles without creating a direct Claude connection.
- Support GitHub-based collaboration between Codex, Claude, and ChatGPT.

Desktop Agent V1 is the first real execution Agent. It is limited to safe macOS application lifecycle management. Browser, terminal, Spotify, Gmail, GitHub, voice, and vision control remain safe placeholders unless explicitly implemented later.

Claude's Living Eye visual identity has now been added as the authoritative design artifact. Codex still owns the application shell, state management, Brain connection, theme tokens, and event bridge. The live Tkinter shell still renders a placeholder Eye until a UI-hosting decision is made for embedding the HTML/SVG prototype.

## What Has Been Done

### 1. Collaboration-Ready Repository

The repository was organized so multiple AI assistants can work through GitHub as the shared source of truth.

Created and structured:

- `core/`
- `brain/`
- `agents/`
- `memory/`
- `voice/`
- `vision/`
- `skills/`
- `plugins/`
- `docs/`
- `prompts/`
- `tests/`
- `scripts/`
- `config/`
- `assets/`
- `logs/`

Added collaboration documents:

- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/api.md`
- `docs/ai_handoff.md`
- `docs/ai_inbox.md`
- `docs/decisions.md`
- `docs/coding_rules.md`
- `docs/memory_model.md`
- `docs/claude_review_findings.md`

Added AI role prompts:

- `prompts/codex.md`
- `prompts/claude.md`
- `prompts/chatgpt.md`

### 2. GitHub Collaboration Layer

GitHub is the collaboration layer for all assistants.

Public repository:

```text
https://github.com/edentiram72-1/nela
```

Important branches:

- `main`: stable baseline.
- `develop`: integration baseline.
- `feature/NELA-0001-foundation-architecture`: initial foundation architecture and Phase 1 Brain.
- `feature/NELA-0002-confirmation-deadlock`: confirmation hardening branch.
- `feature/NELA-0005-desktop-agent-v1`: first real Desktop Agent branch.
- `feature/NELA-0006-ui-foundation`: UI foundation branch.
- `feature/NELA-0007-ai-inbox`: AI collaboration inbox branch.
- `feature/NELA-0011-visual-identity`: Claude Living Eye and design system branch.

Claude does not connect directly to Codex or to the local machine. Claude reviews GitHub branches, direct blob links, pull request diffs, or generated Markdown review bundles.

Use `docs/ai_inbox.md` as the shared GitHub inbox for Claude, Codex, and ChatGPT. For GitHub Issues, use the `AI Collaboration Inbox` issue template.

### 3. Phase 1 Brain Foundation

The first Brain foundation has been implemented.

Main modules:

- `brain/conversation.py`: conversation orchestration.
- `brain/intent_router.py`: deterministic intent recognition.
- `brain/decision.py`: decision making.
- `brain/planner.py`: intent-to-task planning.
- `brain/context.py`: conversation, task, desktop, and confirmation state.
- `brain/dispatcher.py`: task delegation to Agents.
- `brain/memory_manager.py`: short-term and long-term memory orchestration.
- `brain/reasoning.py`: reasoning primitives.

The Brain can now process a request through this flow:

```text
User Input
  |
  v
Conversation Engine
  |
  v
Intent Router
  |
  v
Decision Engine
  |
  v
Planner
  |
  v
Agent Dispatcher
  |
  v
Agent
```

### 4. Event-Driven Runtime

Core event primitives were added in `core/events.py`.

Current lifecycle events include:

- `InputReceived`
- `IntentRecognized`
- `DecisionMade`
- `ConfirmationRequested`
- `ConfirmationResolved`
- `ConfirmationExpired`
- `PlanCreated`
- `TaskCreated`
- `TaskDispatched`
- `TaskStarted`
- `TaskCompleted`
- `TaskFailed`
- `TaskCancelled`
- `AgentStatusChanged`
- `AgentUnavailable`
- `MemoryUpdated`
- `MemoryRetrieved`
- `ContextUpdated`
- `ConversationEnded`

The Event Bus is synchronous and in-process for now. Event hardening is a future task.

### 5. Agent Contract And Agents

All Agents share one contract from `agents/base.py`:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

Implemented Agents:

- Desktop: real macOS application lifecycle management for supported apps.
- Terminal
- Browser
- Voice
- Vision
- Memory
- Spotify
- Files
- Calendar
- Gmail
- GitHub
- Codex
- Claude
- Automation

All non-Desktop Agents currently validate delegation and lifecycle behavior through safe mock behavior. They do not perform real side effects.

### Desktop Agent V1

Desktop Agent V1 replaces the previous Desktop mock with a real macOS lifecycle Agent.

Supported actions:

- launch a supported application
- detect whether a supported application is running
- bring a running supported application to the foreground
- gracefully close a supported application
- return structured execution results with status, application, action, and execution time

Supported applications:

- Google Chrome
- Safari
- Finder
- VS Code
- Spotify
- Terminal

Safety limits:

- no force kill
- no arbitrary shell commands
- no file modification
- no administrator privileges
- no destructive actions
- application lifecycle management only

### 6. Claude Review Workflow

Claude collaboration was prepared without any direct Claude connection.

Implemented:

- `agents/claude/agent.py`
- `scripts/export_claude_review_bundle.py`
- generated review bundle workflow
- `docs/claude_review_findings.md`

Claude reviewed the Phase 1 Brain and identified the next hardening tasks:

- `NELA-0002-confirmation-deadlock`
- `NELA-0003-dispatcher-timeout-retry-safety`
- `NELA-0004-task-idempotency`
- Event Bus hardening
- Intent matching hardening
- Permission policy
- Capability registry
- Plan execution semantics

### 7. NELA-0002: Confirmation Deadlock Fix

The deterministic confirmation deadlock was fixed.

Problem:

- The Brain asked for confirmation.
- Follow-up replies were classified as new input.
- `resolve_confirmation()` was never called.
- The conversation could remain stuck in `WAIT`.

Implemented behavior:

- Pending confirmations are handled before new intent classification.
- Affirmative replies such as `yes`, `confirm`, `do it`, and Hebrew equivalents resume the original Intent.
- Negative replies such as `no`, `cancel`, and Hebrew equivalents cancel the pending action.
- Unclear replies re-ask once.
- Repeated unclear replies cancel the confirmation.
- Expired confirmations are cancelled after a configurable TTL.
- New events were added for confirmation lifecycle tracking.

Architecture decision:

- `DEC-0005`: store the original Intent in `PendingConfirmation.metadata`, then create a fresh Plan after confirmation.

### 8. Dispatcher Timeout And Retry Hardening

Dispatcher timing has started to be hardened.

Current behavior:

- Timeout is tracked per attempt.
- A slow successful synchronous Agent result is not rewritten into a failure after completion.
- Failed attempts that exceed timeout metadata report timeout.
- Retry success is covered by tests.

Remaining work:

- Add idempotency metadata before retrying side-effectful tasks.
- Keep timeout metadata advisory until execution can become cancellable.

### 9. Intent Matching Improvement

Intent matching now checks full keywords and phrases instead of arbitrary substrings.

This prevents false positives such as matching `play` inside `display`.

### 10. Documentation And Traceability

Added and updated:

- architecture documentation
- API documentation
- roadmap
- memory model
- coding rules
- AI handoff file
- Claude review findings
- architecture decisions
- module README files
- GitHub issue and pull request templates

Every significant change should update `docs/ai_handoff.md`.

### 11. Phase 2 UI Foundation

The desktop UI foundation lives under `ui/`.

It provides infrastructure only:

- `ui/app.py`: UI launch entry point.
- `ui/window.py`: Tkinter desktop shell.
- `ui/router.py`: routes UI text input into the existing Brain.
- `ui/state.py`: UI state manager for chat, Eye state, Brain status, Agent activity, notifications, voice flags, and theme selection.
- `ui/events.py`: subscribes to Brain events and maps them to UI state changes.
- `ui/theme.py`: theme token system for dark, light, and future psychedelic themes.
- `ui/animations.py`: state-based animation hooks.
- `ui/components/`: placeholder components for chat, sidebar, status, voice, Eye, and settings.
- `ui/assets/`: future runtime asset slots.

The live Tkinter NELA Eye is state-only for now. Supported states now align with Claude's design system:

- `IDLE`
- `LISTENING`
- `THINKING`
- `SPEAKING`
- `EXECUTING`
- `WAITING`
- `SUCCESS`
- `WARNING`
- `ERROR`
- `SLEEPING`
- `OFFLINE`

Claude can replace the placeholder Eye rendering with the Living Eye prototype without changing the Brain connection.

### 12. Claude Visual Identity: Living Eye

Claude delivered NELA's visual identity package. It has been placed in:

- `design/nela_living_eye.html`: dependency-free animated Living Eye prototype.
- `design/nela_app_icon.svg`: app and dock icon.
- `design/nela_menubar_icon.svg`: macOS menu-bar template icon.
- `docs/design_system.md`: authoritative design system for colors, typography, motion, states, icons, and UI rules.

The Living Eye is driven by one state value. The current UI Event Bridge maps Brain events to Eye states according to the design system:

- `InputReceived`: `listening`
- `IntentRecognized`, `DecisionMade`: `thinking`
- `TaskDispatched`, `TaskStarted`: `executing`
- `ConfirmationRequested`: `waiting`
- `TaskCompleted`: `success`
- `TaskFailed`, `AgentUnavailable`: `error`
- `ConversationEnded`: `idle`

`success`, `warning`, and `error` are moment states. When a UI host provides scheduling, they return to `idle` after 3 seconds.

## Repository Map

| Path | Purpose |
| --- | --- |
| `core/` | App startup, configuration, events, logging, and shared runtime primitives. |
| `brain/` | Conversation orchestration, intent recognition, decisions, planning, context, memory orchestration, and dispatch coordination. |
| `agents/` | Independent execution Agents and the shared Agent contract. |
| `ui/` | Desktop UI shell, state manager, event bridge, theme tokens, animation hooks, and component placeholders. |
| `design/` | Claude Living Eye prototype, app icon, and menu-bar icon. |
| `memory/` | Short-term memory, long-term memory, vector storage, and user profile primitives. |
| `voice/` | Wake word, microphone, speech-to-text, and text-to-speech interfaces. |
| `vision/` | Screen capture, screen reading, OCR, and UI detection interfaces. |
| `skills/` | Future reusable capabilities. |
| `plugins/` | Future installable capability packages. |
| `docs/` | Architecture, roadmap, API notes, coding rules, memory model, decisions, Claude findings, design system, and handoff. |
| `prompts/` | Role prompts for Codex, Claude, and ChatGPT. |
| `tests/` | Unit and integration tests. |
| `scripts/` | Developer utilities, including Claude review bundle export. |
| `config/` | Configuration defaults and templates. |
| `assets/` | Sounds, voices, and future media assets. |
| `logs/` | Runtime log output. Log files are ignored by Git. |

## Run NELA

Interactive text session:

```bash
python3 -m core.app
```

One-shot Brain run with mock dispatch:

```bash
python3 -m core.app --once "Open Spotify and play my Night playlist"
```

One-shot plan inspection without dispatch:

```bash
python3 -m core.app --once "Open Spotify and play my Night playlist" --no-dispatch
```

Desktop UI shell:

```bash
python3 -m ui.app
```

Headless UI bootstrap check:

```bash
python3 -m ui.app --headless-smoke
```

Exit interactive mode:

```text
exit
```

## Run Tests

```bash
python3 -m unittest discover -s tests
```

Current validation status:

```text
All tests passed.
```

## Claude Review Workflow

Option 1: use GitHub links.

Send Claude direct links to branch, diff, or specific blob files.

Current branch:

```text
https://github.com/edentiram72-1/nela/tree/feature/NELA-0006-ui-foundation
```

Option 2: generate a review bundle.

```bash
python3 -m scripts.export_claude_review_bundle
```

Then paste or upload:

```text
docs/claude_review_bundle.md
```

Claude should review architecture, risks, documentation, edge cases, and implementation safety. Claude should not directly rewrite completed modules without justification.

## AI Inbox Workflow

Use the GitHub inbox when work needs to move between assistants:

- `docs/ai_inbox.md`: shared queue with lanes for Claude, Codex, ChatGPT, blocked work, and done work.
- GitHub Issues: use the `AI Collaboration Inbox` issue template.
- Claude review requests should prefer direct `blob/` links.
- Broad reviews can use `docs/claude_review_bundle.md`.
- Do not put secrets, private data, passwords, API keys, or credentials in the inbox.

## AI Collaboration Rules

### Codex

Codex is responsible for:

- implementation
- bug fixing
- tests
- refactoring
- keeping documentation synchronized with code

Codex must not change architecture without documentation.

### Claude

Claude is responsible for:

- architecture review
- documentation review
- edge-case discovery
- UX suggestions
- risk analysis
- performance suggestions

Claude should review through GitHub links, pull requests, or review bundles.

### ChatGPT

ChatGPT is responsible for:

- architecture definition
- system design
- development coordination
- major structural approval

## Development Rules

- One feature per branch.
- Small commits.
- Update documentation with every feature.
- Keep modules independent.
- Never modify unrelated code.
- Add tests whenever practical.
- Keep execution logic inside Agents.
- Keep the Brain agent-neutral.
- Update `docs/ai_handoff.md` before handoff.
- Record major structural decisions in `docs/decisions.md`.

## Current Known Limitations

- Desktop Agent V1 can control supported macOS application lifecycle actions. Other Agents are safe mock placeholders and do not control real applications yet.
- Claude's visual identity artifacts are present under `design/`, but the live Tkinter shell still uses a placeholder Eye component.
- Intent recognition is deterministic and rule-based.
- Event Bus is synchronous and in-process.
- Long-term memory is in-memory only and not durable.
- Timeout metadata cannot interrupt a blocking synchronous Agent yet.
- Desktop lifecycle actions are intentionally narrow. Broader task retries still need idempotency metadata before additional real side effects are allowed.
- A central permission policy is not implemented yet.
- Plugin loading is not implemented yet.
- Parallel and conditional task execution are represented in the model but not fully executed.

## Next Recommended Work

Before real external Agents are enabled:

1. Add task idempotency metadata.
2. Add a permission policy for terminal, desktop, browser, files, accounts, and communication actions.
3. Harden the Event Bus with subscriber isolation and bounded history.
4. Improve capability registry metadata.
5. Simplify the dual memory path for `Remember` requests.
6. Update diagrams to show the Decision Engine and Dispatcher explicitly.

Next UI work should decide how to host `design/nela_living_eye.html` in the live app, such as WebView, Electron, Tauri, or another native wrapper. Codex should continue wiring infrastructure and safety layers without redesigning Claude-owned visuals.

## First Step For Any AI Assistant

1. Read `docs/ai_handoff.md`.
2. Read `docs/architecture.md`.
3. Read `docs/coding_rules.md`.
4. Check the active Git branch.
5. Review recent commits.
6. Confirm the current task and target module.
7. Update `docs/ai_handoff.md` before stopping work.
