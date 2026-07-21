# Brain Module

## Purpose

The Brain is the central orchestrator of NELA OS. It receives user input, recognizes intent, makes decisions, creates plans, updates memory, and delegates work to Agents.

The Brain must never perform desktop, browser, file, service, or plugin actions directly.

## Responsibilities

- Maintain conversation flow.
- Preserve session context.
- Recognize structured intent.
- Decide whether to ask, wait, remember, or delegate.
- Convert intents into executable plans.
- Dispatch tasks through the Agent Dispatcher.
- Publish important lifecycle events.

## Public API

- `ConversationEngine.handle_text(text)`
- `ConversationEngine.handle_voice(transcript)`
- `ConversationEngine.end_conversation()`
- `IntentRouter.classify(text, context=None)`
- `Planner.create_plan(intent)`
- `Planner.cancel_plan(plan)`
- `DecisionEngine.decide(intent, context)`
- `AgentDispatcher.register_agent(agent)`
- `AgentDispatcher.unregister_agent(name)`
- `AgentDispatcher.discover_agents()`
- `AgentDispatcher.health_check()`

## Events

- `InputReceived`
- `IntentRecognized`
- `DecisionMade`
- `PlanCreated`
- `TaskCreated`
- `TaskDispatched`
- `TaskStarted`
- `TaskCompleted`
- `TaskFailed`
- `TaskCancelled`
- `AgentUnavailable`
- `MemoryUpdated`
- `ConversationEnded`

## Known Limitations

- Intent recognition is deterministic and rule-based.
- Parallel task execution is represented in the model but not yet executed concurrently.
- Conditional tasks are represented in the model but do not yet evaluate expressions.
- Agents are placeholders and do not perform real desktop actions yet.

## Future Improvements

- LLM-backed intent recognition.
- Policy-aware reasoning.
- True parallel task execution.
- Conditional expression evaluation.
- Persistent task state.
- User confirmation workflow.

