"""Phrase selection with weighting, tone matching, and repetition avoidance."""

from __future__ import annotations

import random

from language.context import LanguageRuntimeContext
from language.fallback import fallback_phrase
from language.models import LanguagePack, PersonalityProfile, PhraseEntry


class PhraseSelector:
    """Selects a suitable phrase without relying on unrestricted random choice."""

    def __init__(self, seed: int | None = None) -> None:
        self._random = random.Random(seed)

    def select(
        self,
        pack: LanguagePack,
        context: LanguageRuntimeContext,
        personality: PersonalityProfile,
        category: str,
        tone: str | None = None,
        emotion: str | None = None,
        tags: tuple[str, ...] = (),
    ) -> PhraseEntry:
        candidates = [entry for entry in pack.enabled_entries() if entry.category == category]
        if not candidates:
            prefix = category.rsplit(".", 1)[0]
            candidates = [entry for entry in pack.enabled_entries() if entry.category.startswith(prefix)]
        if not candidates:
            selected = fallback_phrase(category, language=pack.language)
            context.remember_phrase(selected.id)
            return selected

        preferred_tone = tone or (personality.preferred_tones[0] if personality.preferred_tones else None)
        preferred_emotion = emotion or (personality.preferred_emotions[0] if personality.preferred_emotions else None)
        ranked = sorted(
            candidates,
            key=lambda entry: self._score(entry, context, personality, preferred_tone, preferred_emotion, tags),
            reverse=True,
        )
        top_score = self._score(ranked[0], context, personality, preferred_tone, preferred_emotion, tags)
        top_candidates = [
            entry
            for entry in ranked
            if self._score(entry, context, personality, preferred_tone, preferred_emotion, tags) >= top_score - 1.0
        ]
        non_recent = [entry for entry in top_candidates if not context.was_recent(entry.id)]
        pool = non_recent or top_candidates
        selected = self._weighted_choice(pool, personality)
        context.remember_phrase(selected.id)
        return selected

    def _score(
        self,
        entry: PhraseEntry,
        context: LanguageRuntimeContext,
        personality: PersonalityProfile,
        tone: str | None,
        emotion: str | None,
        tags: tuple[str, ...],
    ) -> float:
        score = entry.weight
        if tone and tone in entry.tone:
            score += 3.0
        if set(entry.tone) & set(personality.preferred_tones):
            score += 1.5
        if emotion and entry.emotion == emotion:
            score += 2.0
        if entry.emotion in personality.preferred_emotions:
            score += 0.5
        if entry.gender == context.gender == personality.gender:
            score += 0.5
        if tags and set(tags) <= set(entry.tags):
            score += 1.0
        if context.was_recent(entry.id):
            score -= 4.0
        score *= personality.phrase_bias.get(entry.category, 1.0)
        return score

    def _weighted_choice(self, entries: list[PhraseEntry], personality: PersonalityProfile) -> PhraseEntry:
        weights = [max(0.01, entry.weight * personality.phrase_bias.get(entry.category, 1.0)) for entry in entries]
        return self._random.choices(entries, weights=weights, k=1)[0]
