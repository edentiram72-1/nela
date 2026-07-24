"""Application alias resolution for user-facing intents."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationAlias:
    canonical_name: str
    bundle_id: str
    aliases: tuple[str, ...]


SUPPORTED_APPLICATION_ALIASES: tuple[ApplicationAlias, ...] = (
    ApplicationAlias("Spotify", "com.spotify.client", ("spotify", "ספוטיפיי", "ספוטי")),
    ApplicationAlias("Google Chrome", "com.google.Chrome", ("chrome", "google chrome", "כרום")),
    ApplicationAlias("VS Code", "com.microsoft.VSCode", ("vs code", "vscode", "visual studio code", "קוד")),
    ApplicationAlias("Terminal", "com.apple.Terminal", ("terminal", "טרמינל", "מסוף")),
    ApplicationAlias("Finder", "com.apple.finder", ("finder", "פיינדר")),
    ApplicationAlias("Safari", "com.apple.Safari", ("safari", "ספארי")),
)


def resolve_application_alias(value: str | None) -> str | None:
    if not value:
        return None
    normalized = _normalize(value)
    for app in SUPPORTED_APPLICATION_ALIASES:
        names = (_normalize(app.canonical_name), *(_normalize(alias) for alias in app.aliases))
        if normalized in names:
            return app.canonical_name
    return value.strip() or None


def application_bundle_id(value: str | None) -> str | None:
    canonical = resolve_application_alias(value)
    if not canonical:
        return None
    normalized = _normalize(canonical)
    for app in SUPPORTED_APPLICATION_ALIASES:
        if _normalize(app.canonical_name) == normalized:
            return app.bundle_id
    return None


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace(".", "").strip().split())
