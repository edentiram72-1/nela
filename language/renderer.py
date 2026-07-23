"""Template rendering for language phrases."""

from __future__ import annotations

from string import Formatter
from typing import Any


class SafeVariables(dict[str, Any]):
    """Keeps missing variables visible without crashing rendering."""

    def __missing__(self, key: str) -> str:
        return "{" + key + "}"


def template_variables(text: str) -> set[str]:
    variables: set[str] = set()
    for _, field_name, _, _ in Formatter().parse(text):
        if field_name:
            variables.add(field_name.split(".", 1)[0].split("[", 1)[0])
    return variables


def render_template(text: str, variables: dict[str, Any] | None = None) -> str:
    return text.format_map(SafeVariables(variables or {}))


def missing_template_variables(text: str, variables: dict[str, Any] | None = None) -> tuple[str, ...]:
    provided = set((variables or {}).keys())
    return tuple(sorted(template_variables(text) - provided))
