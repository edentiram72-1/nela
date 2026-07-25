# Claude Review Bundle: Language Learning, Defensive Routing, And Visual Prototype

## Review Scope

Branch: `codex/nela-language-learning-cyber`

Repository: `https://github.com/edentiram72-1/nela`

This bundle is for a focused Claude review of the current branch. Do not review
old `develop` state as if it were the latest work.

## What Changed

- Added deterministic Hebrew Q&A for identity, capabilities, connected Agents,
  status, greetings, thanks, and honest unknown-answer handling.
- Added local runtime language learning through `LearningAgent` and
  `language/learning_store.py`.
- Added defensive-only cyber/security routing for safe explanations, passive
  review, threat-model scaffolding, local lab status, local target registration,
  and local-only fuzz planning.
- Added a local browser prototype host for the Living Eye that routes chat
  messages through the existing Brain.
- Added per-launch token and same-origin verification for the local prototype
  bridge.

## What Did Not Change

- No direct Claude connection was added.
- No Coding Agent implementation was added.
- No unrestricted Cyber Agent capability was added.
- No Browser, Terminal, Files, Gmail, GitHub, or communication side effects were
  enabled.
- The Brain still delegates through Agents and does not execute external actions
  directly.
- The local browser prototype is not the final production WebView host.

## Security Notes

- The browser prototype binds to `127.0.0.1` only.
- `/api/chat` rejects requests without `X-NELA-Launch-Token`.
- `/api/chat` rejects requests whose `Origin` is not the expected local origin.
- Cyber/security routing remains defensive and local-lab scoped.
- Active cyber execution remains blocked behind authorization, scoped sessions,
  confirmations, audit logging, process isolation, and kill switch controls.

## Files To Review First

- `brain/qa.py`
- `brain/intent_router.py`
- `brain/planner.py`
- `agents/learning/agent.py`
- `language/learning_store.py`
- `language/hebrew/general_chat.json`
- `core/response.py`
- `ui/web.py`
- `ui/app.py`
- `design/nela_living_eye.html`
- `docs/ai_handoff.md`
- `docs/ai_inbox.md`
- `docs/decisions.md`
- `docs/language_system.md`
- `docs/cyber_lab.md`

## Tests

Latest local validation:

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result:

```text
Language pack validation passed.
144 tests passed.
UI headless smoke passed.
```

## Review Questions For Claude

1. Does the Hebrew conversation behavior match NELA's personality and tone?
2. Are the new Q&A categories enough for a first usable assistant demo?
3. Does the learning flow feel safe and understandable to the user?
4. Are any user-facing Hebrew responses awkward, too technical, or too generic?
5. Are the defensive cyber routing boundaries clear enough before any real
   execution is enabled?
6. Is the token-authenticated local browser prototype acceptable as an interim
   demo host before the production WebView decision?
7. What additional language categories should exist before connecting more
   Agents?

## Known Limitations

- Conversation QA is deterministic and local, not LLM-backed.
- Learned responses are local runtime data and are not yet backed by durable
  long-term memory architecture.
- The local browser prototype is an interim demo host.
- Production WebView, durable audit retention, full async cancellation, plugin
  loading, and real high-risk Agents remain future work.
