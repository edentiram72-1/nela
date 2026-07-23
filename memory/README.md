# Memory Module

## Purpose

Memory stores session context, durable user knowledge, semantic records, and user profile information.

## Responsibilities

- Keep current conversation state available.
- Store long-term memories when approved.
- Prepare for vector-based retrieval.
- Track user profile preferences and projects.

## Public API

- `ShortTermMemory.add_turn(user_text, intent)`
- `ShortTermMemory.recent(limit=10)`
- `LongTermMemory.remember(content, tags=())`
- `LongTermMemory.all()`
- `VectorStore.upsert(record)`
- `VectorStore.get(record_id)`
- `UserProfile.set_preference(key, value)`

## Events

Memory lifecycle events are emitted by `brain/memory_manager.py`:

- `MemoryUpdated`
- `MemoryRetrieved`

## Known Limitations

- Memory is in-process only.
- No persistence backend exists yet.
- No privacy or approval workflow exists yet.

## Future Improvements

- Encrypted local persistence.
- Memory approval UI.
- Project-scoped memories.
- Semantic search.
- Memory pruning and summarization.

