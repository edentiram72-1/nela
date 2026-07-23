"""Safe fallback phrases for missing language-pack entries."""

from __future__ import annotations

from language.models import PhraseEntry


def fallback_phrase(category: str, language: str = "he") -> PhraseEntry:
    text = "אני מטפלת בזה."
    if category.endswith("error") or ".error" in category:
        text = "משהו לא הסתדר, אבל אני עדיין כאן."
    elif category.endswith("clarification") or "clarification" in category:
        text = "אפשר לחדד לי מה לעשות?"
    elif category.endswith("permission") or "permission" in category:
        text = "צריך אישור לפני שאמשיך."
    return PhraseEntry(
        id=f"fallback.{language}.{category}",
        text=text,
        category=category,
        language=language,
        tone=("calm",),
        emotion="neutral",
        tags=("fallback",),
        weight=0.1,
    )
