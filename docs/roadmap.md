# NELA OS Roadmap

## Current Milestone

**Phase 1: Build The Brain**

Goal: Establish the permanent Brain foundation for NELA OS. The Brain thinks, plans, remembers, and delegates. It never performs actions directly.

## Completed Foundation Work

- Collaboration-ready repository structure.
- GitHub issue and pull request templates.
- Central event bus.
- Runtime configuration and logging.
- Brain conversation engine.
- Intent recognition.
- Planner with sequential task dependencies, retry metadata, timeout metadata, and cancellation support.
- Decision engine.
- Context engine.
- Memory manager with short-term and long-term layers.
- Agent dispatcher with dynamic registration APIs.
- Placeholder Agents using a shared lifecycle contract.
- Unit tests for Brain foundation modules.

## Phase 1: Brain Foundation

Status: In progress.

Scope:

- Conversation Engine.
- Intent Recognition.
- Planner.
- Memory Manager.
- Agent Dispatcher.
- Event Bus.
- Decision Engine.
- Context Engine.
- Plugin-ready Agent registration.
- Logging and observability.
- Unit tests.
- Module documentation.

## Phase 2: First Real Agents

Goal: Implement real execution behind selected Agents while keeping the Brain agent-neutral.

Candidate Agents:

- Desktop Agent.
- Terminal Agent.
- Browser Agent.
- Files Agent.

Requirements:

- Permissions and safety policy.
- Integration tests for critical workflows.
- Event-based task status reporting.
- No Brain changes for agent-specific behavior unless the generic contract changes.

## Phase 3: Voice And Vision

Goal: Connect voice input/output and screen understanding.

Scope:

- Wake word.
- Speech-to-text.
- Text-to-speech.
- Screen capture.
- OCR.
- UI detection.
- Context updates from desktop state.

## Phase 4: Memory Persistence

Goal: Add durable local memory.

Scope:

- Encrypted local storage.
- Memory approval flow.
- User profile persistence.
- Project-scoped memory.
- Vector retrieval.

## Phase 5: Plugin System

Goal: Allow capabilities to be installed as plugins.

Examples:

- Weather.
- YouTube.
- Slack.
- WhatsApp.
- Home Assistant.
- iPhone integration.

## Git Strategy

- `main`: stable production-ready history.
- `develop`: integration branch.
- `feature/*`: one feature per branch.
- `bugfix/*`: one bug fix per branch.
- `release/*`: release preparation.

## Task Traceability

Every task should have:

- A branch name.
- A task ID or issue reference.
- A clear target module.
- Acceptance criteria.
- Documentation updates.
- Tests when practical.
- An updated `docs/ai_handoff.md`.

