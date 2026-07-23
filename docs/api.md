# NELA OS API

## Status

Phase 1 exposes internal foundation APIs for the Brain, Agent Dispatcher, Event Bus, and Memory Manager.

These APIs are usable for development and tests, but should still be treated as **Experimental** until the first real Agent integration is complete.

The Hebrew Language Engine and Voice Agent Foundation are also Experimental. They provide the response-output pipeline while Claude continues to own personality and language-content design.

## Stability Levels

| Level | Meaning |
| --- | --- |
| Draft | Early design; breaking changes are expected. |
| Experimental | Usable internally, but still changing. |
| Stable | Safe for other modules to depend on. |
| Deprecated | Scheduled for replacement or removal. |

## Brain APIs

### `ConversationEngine.handle_text(text)`

Module: `brain/conversation.py`
Status: Experimental

Purpose: Process a text request through intent recognition, decision making, planning, memory, and optional delegation.

If a confirmation is pending, the input is routed as a confirmation answer before new intent classification. Affirmative replies resume the original blocked Intent, negative replies cancel it, unclear replies are re-asked once, and expired confirmations are cleared on the next input.

Returns: `ConversationTurn`

Example:

```python
turn = runtime.conversation.handle_text("Open Spotify and play my Night playlist")
```

### `ConversationEngine.handle_voice(transcript)`

Module: `brain/conversation.py`
Status: Experimental

Purpose: Process a voice transcript using the same Brain path as text input.

Returns: `ConversationTurn`

## Runtime CLI

### `python3 -m core.app`

Module: `core/app.py`
Status: Experimental

Purpose: Start an interactive text session with the NELA Brain.

### `python3 -m core.app --once "<request>"`

Module: `core/app.py`
Status: Experimental

Purpose: Process one user request and print the structured Brain summary.

The CLI also prints `NELA Response`, the Hebrew user-facing response rendered by the Language Engine. Voice output can be enabled or silenced through configuration.

Optional flag:

- `--no-dispatch`: create the plan but do not send tasks to Agents.

### `IntentRouter.classify(text, context=None)`

Module: `brain/intent_router.py`
Status: Experimental

Purpose: Convert natural language into a structured `Intent`.

Returns fields such as:

- `action`
- `application`
- `resource`
- `priority`
- `confidence`
- `target_agent`

### `DecisionEngine.decide(intent, context)`

Module: `brain/decision.py`
Status: Experimental

Purpose: Decide whether to ask for clarification, wait, remember, delegate, execute immediately, or reject.

### `Planner.create_plan(intent)`

Module: `brain/planner.py`
Status: Experimental

Purpose: Convert an Intent into executable Tasks.

Planner supports task metadata for:

- Sequential tasks.
- Parallel tasks.
- Conditional tasks.
- Retries.
- Timeouts.
- Cancellation.

### `Planner.cancel_plan(plan)`

Module: `brain/planner.py`
Status: Experimental

Purpose: Return a cancelled copy of a Plan.

## Dispatcher APIs

### `AgentDispatcher.register_agent(agent)`

Module: `brain/dispatcher.py`
Status: Experimental

Purpose: Register an Agent dynamically.

### `AgentDispatcher.unregister_agent(name)`

Module: `brain/dispatcher.py`
Status: Experimental

Purpose: Remove an Agent by name.

### `AgentDispatcher.discover_agents()`

Module: `brain/dispatcher.py`
Status: Experimental

Purpose: List registered Agent names.

### `AgentDispatcher.health_check()`

Module: `brain/dispatcher.py`
Status: Experimental

Purpose: Return health results for all registered Agents.

### `AgentDispatcher.dispatch(task, plan_id)`

Module: `brain/dispatcher.py`
Status: Experimental

Purpose: Send a Task to its target Agent and emit status events.

## Claude Collaboration APIs

### `ClaudeAgent.execute(command)`

Module: `agents/claude/agent.py`
Status: Experimental

Purpose: Prepare Claude review requests and export review bundles without creating a direct connection to Claude.

Supported actions:

- `create_review_request`
- `export_review_bundle`

### `export_bundle(repo_root, output_path, focus, review_files=DEFAULT_REVIEW_FILES)`

Module: `scripts/export_claude_review_bundle.py`
Status: Experimental

Purpose: Create `docs/claude_review_bundle.md`, a Markdown artifact containing instructions, repository metadata, key docs, and selected code files for Claude review.

## Language APIs

### `LanguageEngine.render_response(category, variables=None, tone=None, emotion=None, tags=())`

Module: `language/engine.py`
Status: Experimental

Purpose: Select and render a phrase from the active language pack.

Example:

```python
text = runtime.language.render_response(
    "desktop.open.success",
    {"application": "Spotify"},
)
```

### `LanguageEngine.select_phrase(category, tone=None, emotion=None, tags=())`

Module: `language/engine.py`
Status: Experimental

Purpose: Select a phrase entry using category, weight, recent-use avoidance, personality preferences, tone, emotion, and tags.

### `LanguageEngine.validate_pack(path=None)`

Module: `language/engine.py`
Status: Experimental

Purpose: Validate language pack JSON, required fields, metadata, template variables, and duplicate IDs.

### `python3 -m scripts.validate_language_packs`

Module: `scripts/validate_language_packs.py`
Status: Experimental

Purpose: Validate the Hebrew language pack from the command line.

## Response APIs

### `NelaResponseAdapter.render_turn(turn)`

Module: `core/response.py`
Status: Experimental

Purpose: Convert a semantic `ConversationTurn` into a Hebrew user-facing response without executing actions.

### `NelaResponseAdapter.render_and_maybe_speak(turn)`

Module: `core/response.py`
Status: Experimental

Purpose: Render the same Hebrew response for UI and, when enabled, delegate speech to the Voice Agent through the Dispatcher.

## Voice APIs

### `VoiceAgent.execute(command)`

Module: `agents/voice/agent.py`
Status: Experimental

Purpose: Speak, queue, stop, interrupt, pause, resume, configure, and report status for voice output.

Supported command actions:

- `speak`
- `queue_speech`
- `flush_queue`
- `stop`
- `interrupt`
- `pause`
- `resume`
- `set_enabled`
- `configure_profile`
- `status`

### `SpeechProvider`

Module: `voice/providers/base.py`
Status: Experimental

Purpose: Replaceable provider contract for speech backends.

Current providers:

- `MacOSSpeechProvider`
- `MockSpeechProvider`

### `create_speech_provider(name)`

Module: `voice/providers/factory.py`
Status: Experimental

Purpose: Create a speech provider from configuration.

Supported names:

- `macos_say`
- `mock`

## Agent Contract

Module: `agents/base.py`
Status: Experimental

Every Agent exposes:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

Shared types:

- `AgentCommand`
- `AgentResult`
- `AgentState`
- `BaseAgent`

## Event Bus APIs

### `EventBus.subscribe(event_type, handler)`

Register a handler for a specific event type or `*`.

### `EventBus.publish(event)`

Publish an event to matching subscribers.

### `EventBus.history()`

Return in-memory event history for tests and diagnostics.

Current Brain lifecycle events include:

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
- `AgentUnavailable`
- `MemoryUpdated`
- `MemoryRetrieved`
- `SpeechQueued`
- `SpeechStarted`
- `SpeechPaused`
- `SpeechResumed`
- `SpeechCompleted`
- `SpeechInterrupted`
- `SpeechFailed`
- `VoiceStatusChanged`
- `ConversationEnded`

## Memory APIs

### `MemoryManager.record_turn(user_text, intent)`

Record a conversation turn in short-term memory.

### `MemoryManager.remember(content, tags=())`

Store long-term memory and emit `MemoryUpdated`.

### `MemoryManager.recent_context(limit=10)`

Retrieve recent short-term memory and emit `MemoryRetrieved`.
