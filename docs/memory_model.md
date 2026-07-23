# NELA OS Memory Model

## Purpose

NELA OS separates memory into clear layers so the assistant can remember useful context without mixing temporary conversation state with durable user knowledge.

## Memory Types

### Short-Term Memory

Location: `memory/short_term.py`

Purpose:

- Store current session turns.
- Keep recent user requests and detected intents.
- Support immediate conversational continuity.

Retention:

- In-memory only for now.
- Cleared when the runtime restarts.

### Long-Term Memory

Location: `memory/long_term.py`

Purpose:

- Store durable facts, preferences, project context, and user-approved memories.

Retention:

- In-memory placeholder for now.
- Future implementation should persist to a local database or encrypted file store.

### Vector Memory

Location: `memory/vector_store.py`

Purpose:

- Store embeddings for semantic retrieval.
- Support future search across conversations, files, and project context.

Retention:

- In-memory placeholder for now.
- Future implementation should support a local vector database.

### Profile Memory

Location: `memory/profile.py`

Purpose:

- Store stable user profile fields.
- Store preferences.
- Track active projects.

## Memory Rules

- Do not store secrets in memory.
- Do not persist sensitive data without explicit design approval.
- Keep session memories separate from long-term memories.
- Add events when memory is written or retrieved.
- Document any persistence backend before implementation.

## Current Limitations

- No durable storage exists yet.
- No vector similarity search exists yet.
- No privacy policy or retention policy has been implemented.
- No user approval workflow exists for saving long-term memories.

## Future Improvements

- Local encrypted persistence.
- Memory approval flow.
- Semantic retrieval.
- Project-scoped memory.
- Memory pruning and summarization.
- Import/export tools for user-controlled backup.

