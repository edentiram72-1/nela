"""Helpers for supported language-pack file formats."""

from __future__ import annotations


def language_file_entries(raw: object) -> list[dict[str, object]]:
    """Normalize supported language-pack file shapes into PhraseEntry dicts."""

    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]

    if not isinstance(raw, dict):
        return []

    if isinstance(raw.get("phrases"), list):
        return [item for item in raw["phrases"] if isinstance(item, dict)]

    if isinstance(raw.get("categories"), dict):
        language = str(raw.get("language", "he"))
        version = str(raw.get("version", "1.0"))
        entries: list[dict[str, object]] = []
        for category, category_data in raw["categories"].items():
            if not isinstance(category_data, dict):
                continue
            variants = category_data.get("variants", ())
            if not isinstance(variants, list):
                continue
            category_eye_state = category_data.get("eye_state")
            for variant in variants:
                if not isinstance(variant, dict):
                    continue
                normalized = dict(variant)
                normalized["category"] = str(category)
                normalized["language"] = language
                normalized["version"] = version
                normalized["requires"] = tuple(str(item) for item in variant.get("vars", ()))
                if category_eye_state is not None and "eye_state" not in normalized:
                    normalized["eye_state"] = category_eye_state
                entries.append(normalized)
        return entries

    return []
