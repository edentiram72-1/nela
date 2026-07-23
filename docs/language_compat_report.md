# Language & Voice Foundation — Claude Compatibility Report (PENDING ACCESS)

Status: **blocked on file access.** Branch `feature/NELA-language-voice-foundation`
was announced without blob links; GitHub tree pages are robots-blocked for
Claude, and web search does not index the fresh branch. This report contains
everything that can be produced without the code, and the exact list of what
is needed to finish.

## 1. Links required to complete the review

Paste these as direct blob links (replace nothing — the paths come from the
announcement):

```
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/docs/language_system.md
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/docs/voice_architecture.md
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/language/engine.py        (or actual engine path)
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/language/hebrew/greetings.json   (any one pack file)
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/language/personality/default.json
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/voice/agent.py            (or actual VoiceAgent path)
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/tests/test_language_engine.py
https://github.com/edentiram72-1/nela/blob/feature/NELA-language-voice-foundation/docs/ai_handoff.md
```

Alternative: regenerate the review bundle on that branch —
`python3 -m scripts.export_claude_review_bundle` — and upload it. One pack
file + the engine + the two docs are the minimum.

## 2. Schema compatibility checklist (to verify against the engine)

These are the load-bearing features of the Claude language design
(`language/pack_schema.md`). Each is PASS/FAIL once the code is visible:

| # | Feature | Why it matters | Verify in |
| --- | --- | --- | --- |
| S1 | Variant fields: `id`, `text`, `vars`, `weight`, `min_stage`, `gender_tier`, `eye_state`, `max_per_session`, `cooldown_group`, `time_of_day`, `humor` | The 117 phrases carry these; unknown-field handling (ignore vs reject) decides if files load as-is | engine loader |
| S2 | Gender tag syntax `{you:masc\|fem}` + fallback: unknown gender ⇒ variant ineligible ⇒ tier-1 neutral chosen | Core Hebrew correctness; wrong fallback = wrong grammar to every new user | engine renderer |
| S3 | Anti-repetition: cooldown ring (3), per-session caps, weighted choice | Without it, the "never repeat" personality rule is unenforced | selection logic |
| S4 | Humor budget: max 1/conversation, mood-gated | Personality Bible hard rule | selection logic |
| S5 | `relationship_stage` filter (1–3) sourced from memory/profile | The trust-arc design | engine ↔ memory wiring |
| S6 | Fail-closed variables: missing var ⇒ skip variant, never render a hole | "מנגנת את {resource}" with empty resource is broken Hebrew | renderer |
| S7 | `render_count(n, singular, plural)` Hebrew agreement (1/2/3–10/11+) | "3 תוצאה" is the machine-translation tell | helper |
| S8 | `eye_state` per category/variant, names = the 11 canonical states | Speech and eye must never disagree | engine → UI/state |
| S9 | Personality preset shape: `params` + `pack_overrides.boost` | My default/warm/psychedelic files use this shape | preset loader |
| S10 | No user-facing Hebrew hardcoded in Python (engine or VoiceAgent) | The whole point of packs | grep |

## 3. Voice-specific checks (no code needed for the questions)

- V1: VoiceAgent must consume Language Engine output — never its own strings.
  If any Hebrew literal exists in `voice/`, that is a FAIL on S10.
- V2: `say` on macOS uses the **Carmit** Hebrew voice; quality is serviceable
  for a foundation but fails the tone acceptance test from
  `docs/tone_of_voice.md` ("נתקעתי רגע" must not sound dramatic; Carmit tends
  flat-robotic). Fine for now — record as a known limitation, plan a neural
  TTS provider behind the same provider protocol.
- V3: Silent-by-default is the right call and matches the design (speech is
  opt-in; the eye is the always-on channel). Confirm the toggle is a
  preference (`preferences.set("voice.enabled", ...)`), not a config constant.
- V4: Latin words inside Hebrew sentences ("פותחת את Chrome") — verify `say`
  pronunciation; the packs deliberately place Latin tokens at clause end
  (see `docs/hebrew_language_guide.md` §5), but TTS may still need a
  per-variant `speech_text` override field. If the engine lacks such a field,
  that is the one schema addition I'd request (S11, optional).

## 4. Deliverable files — current state

The repository-ready files already exist and are unchanged in this pass
(adaptation without the target schema would be guesswork):

- `docs/personality_bible.md`, `docs/hebrew_language_guide.md`,
  `docs/tone_of_voice.md`, `docs/conversation_rules.md`
- `language/personality/default.json`, `warm.json`, `psychedelic.json`
- `language/hebrew/` — 10 pack files, 117 variants, JSON-validated
- All in `nela-language-drop.zip` with `APPLY_THIS_DROP.md`

If the checklist passes, these files integrate as-is. Each FAIL becomes either
a one-pass mechanical transform of the JSON (I will produce it within one
review round once I see one example pack from Codex) or a small engine change.

## 5. Instructions for Codex (can start now, no waiting on Claude)

1. Run the S1–S10 checklist yourself against `language/pack_schema.md` — it is
   in the repo drop and is the contract the 117 phrases were written to.
2. Load `nela-language-drop.zip`'s `language/hebrew/*.json` through the engine
   in a test: every file parses, every category selectable, unknown fields
   do not crash. Report per-file results in `docs/ai_handoff.md`.
3. Grep `voice/` and `language/` for hardcoded Hebrew string literals; move
   any found into packs.
4. Answer S9 explicitly: paste the engine's expected preset JSON shape into
   `docs/language_system.md` if it differs from mine.
