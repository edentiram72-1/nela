# NELA OS

English | [עברית](README.he.md)

NELA OS is a desktop-first AI operating system foundation inspired by the idea of a JARVIS-like intelligent assistant.

The project is being built as a modular, event-driven assistant that can grow into voice conversation, memory, computer control, screen understanding, automation, plugin support, multi-agent orchestration, and future mobile integration.

## Mission

Build a maintainable AI operating layer where one central Brain understands requests, reasons about them, creates plans, remembers context, and delegates execution to independent Agents.

The Brain never executes external actions directly. Agents do the work. Modules communicate through events instead of direct cross-module dependencies.

## Current Status

NELA OS is currently in **Phase 1: Build The Brain**.

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
- Use safe mock Agents for MVP validation without controlling real apps.
- Export Claude review bundles without creating a direct Claude connection.
- Support GitHub-based collaboration between Codex, Claude, and ChatGPT.

No real desktop, browser, terminal, Spotify, Gmail, GitHub, voice, or vision control is enabled yet. Current Agents are safe placeholders unless explicitly implemented later.

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
- `feature/NELA-0002-confirmation-deadlock`: current active hardening branch.

Claude does not connect directly to Codex or to the local machine. Claude reviews GitHub branches, direct blob links, pull request diffs, or generated Markdown review bundles.

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

### 5. Agent Contract And Safe Mock Agents

All Agents share one contract from `agents/base.py`:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

Implemented placeholders and mock-backed Agents:

- Desktop
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

These Agents currently validate delegation and lifecycle behavior. They do not perform real side effects.

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

## Repository Map

| Path | Purpose |
| --- | --- |
| `core/` | App startup, configuration, events, logging, and shared runtime primitives. |
| `brain/` | Conversation orchestration, intent recognition, decisions, planning, context, memory orchestration, and dispatch coordination. |
| `agents/` | Independent execution Agents and the shared Agent contract. |
| `memory/` | Short-term memory, long-term memory, vector storage, and user profile primitives. |
| `voice/` | Wake word, microphone, speech-to-text, and text-to-speech interfaces. |
| `vision/` | Screen capture, screen reading, OCR, and UI detection interfaces. |
| `skills/` | Future reusable capabilities. |
| `plugins/` | Future installable capability packages. |
| `docs/` | Architecture, roadmap, API notes, coding rules, memory model, decisions, Claude findings, and handoff. |
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
https://github.com/edentiram72-1/nela/tree/feature/NELA-0002-confirmation-deadlock
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

- Agents are safe mock placeholders and do not control real applications yet.
- Intent recognition is deterministic and rule-based.
- Event Bus is synchronous and in-process.
- Long-term memory is in-memory only and not durable.
- Timeout metadata cannot interrupt a blocking synchronous Agent yet.
- Task retries still need idempotency metadata before real side effects are allowed.
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

After these safety layers, begin the first real Agent implementation, likely Desktop, Terminal, Browser, or Files.

## First Step For Any AI Assistant

1. Read `docs/ai_handoff.md`.
2. Read `docs/architecture.md`.
3. Read `docs/coding_rules.md`.
4. Check the active Git branch.
5. Review recent commits.
6. Confirm the current task and target module.
7. Update `docs/ai_handoff.md` before stopping work.
