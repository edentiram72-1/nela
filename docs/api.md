# NELA OS API

## Status

Phase 1 exposes internal foundation APIs for the Brain, Agent Dispatcher, Event Bus, and Memory Manager.

These APIs are usable for development and tests, but should still be treated as **Experimental** until the first real Agent integration is complete.

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

## Memory APIs

### `MemoryManager.record_turn(user_text, intent)`

Record a conversation turn in short-term memory.

### `MemoryManager.remember(content, tags=())`

Store long-term memory and emit `MemoryUpdated`.

### `MemoryManager.recent_context(limit=10)`

Retrieve recent short-term memory and emit `MemoryRetrieved`.

