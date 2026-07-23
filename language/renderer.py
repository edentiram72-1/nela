"""Template rendering for language phrases."""

from __future__ import annotations

import re
from string import Formatter
from typing import Any

GENDER_TAG = re.compile(r"\{you:([^{}|]+)\|([^{}|]+)\}")


class SafeVariables(dict[str, Any]):
    """Keeps missing variables visible without crashing rendering."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def template_variables(text: str) -> set[str]:
    text = GENDER_TAG.sub("", text)
    variables: set[str] = set()
    for _, field_name, _, _ in Formatter().parse(text):
        if field_name:
            variables.add(field_name.split(".", 1)[0].split("[", 1)[0])
    return variables


def render_template(text: str, variables: dict[str, Any] | None = None) -> str:
    values = variables or {}

    def replace_gender(match: re.Match[str]) -> str:
        gender = str(values.get("user_gender", values.get("gender", "unknown"))).lower()
        if gender in {"m", "male", "masculine"}:
            return match.group(1)
        if gender in {"f", "female", "feminine"}:
            return match.group(2)
        return match.group(1)

    return GENDER_TAG.sub(replace_gender, text).format_map(SafeVariables(values))


def missing_template_variables(text: str, variables: dict[str, Any] | None = None) -> tuple[str, ...]:
    provided = set((variables or {}).keys())
    return tuple(sorted(template_variables(text) - provided))
