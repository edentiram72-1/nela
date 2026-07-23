# NELA Language Pack Schema

Technical companion to `docs/nela_personality.md` (Hebrew, authoritative for
*content*). This document is authoritative for *structure*: how phrases are
stored, selected, and scaled to 10,000+ without repetition. Audience: Codex.

## 1. Design goals

1. **Thousands of variants, zero hardcoded strings.** No Python file ever
   contains user-facing Hebrew. Everything lives in packs.
2. **No repetition.** The selection engine statistically prevents the same
   phrase twice in a row and caps per-session reuse.
3. **Hebrew gender correctness.** NELA always speaks feminine first-person.
   User-directed morphology resolves through a two-tier system (neutral
   phrasing by default, gendered forms when `profile.gender` is known).
4. **Emotion-aware.** Every phrase is tagged with the eye state it accompanies,
   so voice, text, and the eye always agree.
5. **Relationship-aware.** Phrases unlock by `relationship_stage` (1–3).

## 2. File layout

```text
language/
  packs/
    core.he.json          # greetings, acks, thinking, success, errors...
    desktop.he.json       # desktop/app-control phrases
    media.he.json         # music & playback
    memory.he.json        # remembering/recall phrases
    smalltalk.he.json     # daily conversation, humor
    system.he.json        # notifications, warnings, voice wake
  pack_schema.md          # this file
```

One pack per domain. Packs are additive; loading order never matters because
ids are globally unique (`<pack>.<category>.<slug>`).

## 3. Pack format

```json
{
  "pack": "core",
  "language": "he",
  "version": 1,
  "categories": {
    "success.short": {
      "description": "Task finished, minimal ack",
      "eye_state": "success",
      "variants": [
        { "id": "core.success.yesh", "text": "יש." },
        { "id": "core.success.smooth", "text": "הלך חלק." },
        { "id": "core.success.done", "text": "זהו, מוכן." },
        { "id": "core.success.signature", "text": "סגור. {task_hint}", "vars": ["task_hint"], "weight": 0.5 }
      ]
    }
  }
}
```

### Variant fields

| Field | Required | Meaning |
| --- | --- | --- |
| `id` | yes | Globally unique. `<pack>.<category-slug>.<name>` |
| `text` | yes | The Hebrew phrase. May contain `{variables}` and gender tags |
| `vars` | if used | Declared variables; engine rejects render with missing vars |
| `weight` | no (1.0) | Relative selection probability |
| `min_stage` | no (1) | Minimum `relationship_stage` (1–3) |
| `gender_tier` | no (1) | 1 = neutral phrasing, 2 = contains user-gender tags |
| `eye_state` | no | Overrides category default |
| `max_per_session` | no (2) | Hard cap per session |
| `cooldown_group` | no | Variants sharing a group share the no-repeat window |
| `time_of_day` | no | `morning\|day\|evening\|night` filter |
| `humor` | no (false) | Counts against the 1-humor-per-conversation budget |

### Variables

`{application}`, `{query}`, `{count}`, `{resource}`, `{user_name}`,
`{task_hint}`, `{what}` (error cause, plain Hebrew), `{clarify}` (the one
question being asked). Renderer must fail closed: a variant whose variable is
unavailable is skipped, never rendered with a hole.

**Hebrew count agreement:** `{count}` renders via a helper, not raw:
1 → "תוצאה אחת", 2 → "שתי תוצאות", 3–10 → "שלוש/ארבע… תוצאות" (word),
11+ → "12 תוצאות" (digits). The noun's plural form is part of the call site:
`render_count(n, "תוצאה", "תוצאות")`.

### Gender tags (tier 2 only)

Inline syntax: `{you:masculine|feminine}` — e.g. `"{you:תרצה|תרצי} שאמשיך?"`.
Resolution:

```text
profile.gender == "m" → left form
profile.gender == "f" → right form
unknown              → variant is INELIGIBLE (engine falls back to tier-1
                       neutral variants in the same category)
```

Rule enforced by a pack linter: every category MUST contain at least 2
tier-1 (neutral) variants, so the unknown-gender path always has choices.
NELA's own verbs are always feminine and written directly (no tags needed).

## 4. Selection engine

```text
choose(category, context):
  pool = variants[category]
        filtered by: min_stage <= context.stage
                     gender eligibility (see above)
                     time_of_day (if tagged)
                     session_use[id] < max_per_session
                     id not in last_used_ring(cooldown_group, size=3)
                     humor_budget respected
  if pool empty: relax filters in order (humor → time → cooldown) and retry;
                 final fallback = category's first tier-1 variant
  pick weighted-random from pool
  record in last_used_ring + session_use
  return render(text, context.vars)
```

- `last_used_ring` size 3 per cooldown group ⇒ a phrase can't return within
  its next 3 uses of that group. With ≥6 variants per category, perceived
  repetition drops to near zero.
- The engine emits `PhraseSelected {id, category}` on the event sink —
  observability for tuning weights later, and the hook that will let a future
  LLM layer paraphrase around the selected skeleton.

## 5. Category taxonomy (initial — extensible)

`greeting.first_launch · greeting.day · greeting.return · farewell ·
ack.short · ack.ongoing (uses "העין שלי על זה") · confirm.ask ("סגרנו?") ·
clarify.one_question · thinking · waiting · success.short · success.long ·
failure.recoverable · failure.final · error.recovering · warning ·
apology.single · encouragement · humor.dry · compliment.earned ·
learning.saved ("שמרתי אצלי") · memory.recall · desktop.launch ·
desktop.close_confirm · desktop.focus · files · browser · media.play ·
media.search · coding · projects · automation.suggest · smalltalk.daily ·
smalltalk.general · system.notification · voice.wake ("אני איתך") ·
voice.sleep`

Growth rule: a new category needs a `description`, a default `eye_state`, and
≥4 variants (≥2 neutral) before merge. 3,000 phrases ≈ 40 categories × ~75
variants; 10,000+ is the same structure with more packs — no engine changes.

## 6. Integration points

- **Eye:** category/variant `eye_state` values are exactly the 11 states in
  `docs/design_system.md` §3. Emitting a phrase and setting the eye must be
  one call site so they never disagree.
- **Memory:** `relationship_stage`, `profile.gender`, `user_name`, and the
  user's own `CustomPhrase` aliases come from the memory subsystem
  (`memory/profile.py`, `memory/long_term.py`). Stage-3 behavior of echoing
  the user's vocabulary reads `long_term.phrases()`.
- **Brain:** decision/dispatch sites request categories, never strings:
  `speech.say("success.short", task_hint=...)`.

## 7. Anti-goals

- No machine-translated Hebrew. Content is written in Hebrew first, per the
  Personality Bible; never generated by translating English strings.
- No per-phrase code. If a phrase needs logic, the logic belongs in a
  variable or a new category, not in Python string handling.
- No exclamation inflation, no emoji (unless mirroring the user), no
  customer-support register — the linter greps for the forbidden list in
  `nela_personality.md` §1.
