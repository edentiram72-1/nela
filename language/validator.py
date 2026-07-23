"""Validation for language packs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from language.models import PhraseEntry, ValidationIssue, ValidationReport
from language.pack_format import language_file_entries
from language.renderer import template_variables

REQUIRED_FIELDS = {"id", "text", "category", "language"}
SUPPORTED_FIELDS = {
    "id",
    "text",
    "category",
    "language",
    "tone",
    "emotion",
    "formality",
    "gender",
    "weight",
    "requires",
    "tags",
    "enabled",
    "version",
    "speech_text",
    "min_stage",
    "gender_tier",
    "eye_state",
    "max_per_session",
    "cooldown_group",
    "time_of_day",
    "humor",
    "vars",
}


def validate_pack(path: Path | str) -> ValidationReport:
    pack_path = Path(path)
    issues: list[ValidationIssue] = []
    try:
        manifest = json.loads((pack_path / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return ValidationReport((ValidationIssue("invalid_manifest", str(error), file="manifest.json"),))

    entries: list[tuple[str, dict[str, Any]]] = []
    for filename in manifest.get("files", ()):
        file_path = pack_path / str(filename)
        try:
            raw = json.loads(file_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            issues.append(ValidationIssue("invalid_json", str(error), file=str(filename)))
            continue
        phrase_items = language_file_entries(raw)
        if not isinstance(phrase_items, list):
            issues.append(
                ValidationIssue(
                    "invalid_file_shape",
                    "Expected a list, {'phrases': [...]}, or Claude {'categories': {...}} object.",
                    file=str(filename),
                )
            )
            continue
        for item in phrase_items:
            if not isinstance(item, dict):
                issues.append(ValidationIssue("invalid_entry_shape", "Phrase entry must be an object.", file=str(filename)))
                continue
            entries.append((str(filename), item))

    issues.extend(validate_entries(entries, manifest))
    return ValidationReport(tuple(issues))


def validate_entries(entries: list[tuple[str, dict[str, Any]]], manifest: dict[str, Any]) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    categories = set(str(item) for item in manifest.get("categories", ()))
    tones = set(str(item) for item in manifest.get("tones", ()))
    emotions = set(str(item) for item in manifest.get("emotions", ()))
    language = str(manifest.get("language", "he"))

    for filename, data in entries:
        entry_id = str(data.get("id", ""))
        missing = REQUIRED_FIELDS - data.keys()
        if missing:
            issues.append(ValidationIssue("missing_required_fields", f"Missing fields: {', '.join(sorted(missing))}", entry_id or None, filename))
            continue
        if entry_id in seen_ids:
            issues.append(ValidationIssue("duplicate_id", f"Duplicate phrase id: {entry_id}", entry_id, filename))
        seen_ids.add(entry_id)
        try:
            entry = PhraseEntry.from_dict(data)
        except (KeyError, TypeError, ValueError) as error:
            issues.append(ValidationIssue("invalid_entry", str(error), entry_id or None, filename))
            continue
        if not entry.text.strip():
            issues.append(ValidationIssue("empty_text", "Phrase text cannot be empty.", entry.id, filename))
        if entry.language != language:
            issues.append(ValidationIssue("invalid_language", f"Expected language {language}, got {entry.language}.", entry.id, filename))
        if categories and entry.category not in categories:
            issues.append(ValidationIssue("invalid_category", f"Unsupported category: {entry.category}", entry.id, filename))
        unsupported_tones = [tone for tone in entry.tone if tones and tone not in tones]
        if unsupported_tones:
            issues.append(ValidationIssue("unsupported_tone", f"Unsupported tones: {', '.join(unsupported_tones)}", entry.id, filename))
        if emotions and entry.emotion not in emotions:
            issues.append(ValidationIssue("unsupported_emotion", f"Unsupported emotion: {entry.emotion}", entry.id, filename))
        unsupported_fields = sorted(set(data) - SUPPORTED_FIELDS)
        if unsupported_fields:
            issues.append(
                ValidationIssue(
                    "unsupported_fields",
                    f"Unsupported fields preserved in extra_fields: {', '.join(unsupported_fields)}",
                    entry.id,
                    filename,
                    level="warning",
                )
            )
        variables = template_variables(entry.text)
        if entry.speech_text:
            variables |= template_variables(entry.speech_text)
        missing_requires = variables - set(entry.requires)
        if missing_requires:
            issues.append(ValidationIssue("broken_template_variables", f"Template variables not listed in requires: {', '.join(sorted(missing_requires))}", entry.id, filename))
    return tuple(issues)
