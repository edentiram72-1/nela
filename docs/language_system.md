# NELA Language System

## Purpose

The Language System turns semantic Brain output into user-facing Hebrew text.

It does not define NELA's final personality. Claude owns personality, tone, emotional behavior, and language-pack content. Codex owns the technical infrastructure that loads, validates, selects, renders, and safely falls back when language content is missing.

## Flow

```text
Brain semantic result
  |
  v
NelaResponseAdapter
  |
  v
LanguageEngine
  |
  +--> LanguagePackLoader
  +--> PhraseSelector
  +--> TemplateRenderer
  +--> Validator
  |
  v
Final Hebrew response
  |
  +--> UI
  +--> Voice Agent
```

## Public API

Module: `language/engine.py`

- `load_language_pack(path)`: load and validate a pack directory.
- `reload_language_pack()`: reload the current pack from disk.
- `render_response(category, variables=None, tone=None, emotion=None, tags=())`: select and render a phrase.
- `select_phrase(category, tone=None, emotion=None, tags=())`: return the selected `PhraseEntry`.
- `validate_pack(path=None)`: return a validation report.
- `list_categories()`: return supported categories.
- `get_available_tones()`: return available tone names.
- `health_check()`: report pack, personality, and validation status.

## Phrase Model

Each phrase entry supports:

- `id`
- `text`
- `category`
- `language`
- `tone`
- `emotion`
- `formality`
- `gender`
- `weight`
- `requires`
- `tags`
- `enabled`
- `version`

Template variables use Python-style braces, for example:

```json
{
  "id": "desktop.open.success.1",
  "text": "פותחת את {application}.",
  "category": "desktop.open.success",
  "language": "he",
  "tone": ["warm"],
  "emotion": "neutral",
  "requires": ["application"]
}
```

Missing variables are kept visible as `{variable}` instead of crashing the response path.

## Selection Rules

`PhraseSelector` supports:

- category matching
- category-prefix fallback
- weighted variation
- recent-phrase avoidance
- personality profile preferences
- requested tone and emotion
- safe Hebrew fallback phrases

Selection is weighted and scored, not unrestricted random-only choice.

## Validation

Run:

```bash
python3 -m scripts.validate_language_packs
```

The validator detects:

- duplicate IDs
- missing required fields
- invalid JSON
- unsupported categories
- unsupported tones and emotions
- empty text
- language metadata mismatch
- template variables missing from `requires`

## Seed Pack

The first Hebrew pack under `language/hebrew/` is intentionally small. It provides enough phrases to validate system behavior without replacing Claude's future language work.

Current categories include greetings, farewells, confirmations, clarifications, thinking, waiting, success, errors, warnings, apologies, permissions, desktop, files, browser, music, coding, memory, automation, and general chat.

## Adding Hebrew Phrases

1. Choose the category file under `language/hebrew/`.
2. Add a phrase entry with a unique `id`.
3. Include every template variable in `requires`.
4. Use only tones and emotions listed in `language/hebrew/manifest.json`.
5. Run `python3 -m scripts.validate_language_packs`.

New categories require two edits:

1. Add the category name to `language/hebrew/manifest.json`.
2. Add phrases in an existing category file or add a new file and list it in `manifest.json`.

Keep Brain modules unchanged when adding phrases.

## Runtime Learned Responses

NELA can now learn simple user-taught trigger/response pairs at runtime without
editing the core Hebrew pack.

Flow:

```text
User: "נלה תלמדי שכשאני אומר בוקר טוב תעני בוקר אור"
  |
  v
IntentRouter -> TeachResponse
  |
  v
Planner -> learning.teach_response
  |
  v
Permission Engine -> T1 local scoped write
  |
  v
LearningAgent -> data/language/learned_responses.json
  |
  v
KnowledgeEngine answers future matching turns with qa.learned
```

This is intentionally separate from Claude-authored phrase packs:

- Claude/personality packs remain authoritative for NELA's voice.
- User-taught responses are local runtime data.
- The Brain stays semantic and does not hardcode Hebrew responses.
- Learned responses are exact/simple trigger matches in this phase, not an
  unrestricted knowledge base.

Supported examples:

```text
נלה תלמדי שכשאני אומר בוקר טוב תעני בוקר אור
כשאני אומר מצב בית תעני הכל רגוע
learn response: ping => pong
```

Future extensions should add review, editing, deletion, tagging, and conflict
resolution before large-scale phrase ingestion.

## Personality Profiles

Personality profiles under `language/personality/` influence selection with metadata only:

- preferred tones
- preferred emotions
- formality
- gender
- category bias

They do not execute code and should not contain secrets. Claude can replace these profiles with richer rules later as long as they stay data-driven.

## Privacy

The Language System currently reads local JSON files and renders local text. It does not call external APIs, send text to cloud services, or persist conversation text by itself.

Privacy can change if future plugin-based language packs or cloud personalization are added. Any future external language provider must document what text leaves the machine and must not store secrets in language-pack files.

## Future Extensions

- Load language packs from plugins.
- Add pack version migrations.
- Add review tooling for Claude-authored packs.
- Add richer grammatical controls for Hebrew gender, number, and formality.
- Add deterministic phrase snapshots for scripted demos.
- Add runtime pack reload from a settings screen.
