"""Reusable scope validation for Permission Engine decisions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from permissions.models import PermissionRequest, ScopedSession


PROTECTED_PATHS = (
    Path("~/.ssh").expanduser().resolve(),
    Path("~/Library/Keychains").expanduser().resolve(),
    Path("~/Library/Application Support").expanduser().resolve() / "com.apple.security",
)


@dataclass(frozen=True)
class ScopeValidationResult:
    allowed: bool
    reason: str
    normalized_target: str | None = None


def validate_scopes(
    scopes: tuple[str, ...],
    request: PermissionRequest,
    session: ScopedSession | None,
) -> ScopeValidationResult:
    for scope in scopes:
        if scope.startswith("filesystem."):
            result = _validate_filesystem_scope(scope, request, session)
            if not result.allowed:
                return result
            continue
        if session is None or not session.has_scope(scope):
            return ScopeValidationResult(False, f"Missing scoped session grant for scope '{scope}'.")
    return ScopeValidationResult(True, "Scope allowed.")


def _validate_filesystem_scope(
    scope: str,
    request: PermissionRequest,
    session: ScopedSession | None,
) -> ScopeValidationResult:
    target = request.payload.get("path") or request.payload.get("target")
    if not target:
        return ScopeValidationResult(False, f"Scope '{scope}' requires a path target.")

    try:
        canonical = _canonicalize_path(str(target))
    except OSError:
        return ScopeValidationResult(False, "Path target could not be canonicalized safely.")

    if _is_protected_path(canonical):
        return ScopeValidationResult(False, "Protected credential or security path is denied.", str(canonical))

    if session is None:
        return ScopeValidationResult(False, f"Scope '{scope}' requires an active scoped session.", str(canonical))

    allowed_roots = _allowed_values_for_scope(scope, session)
    if not allowed_roots:
        return ScopeValidationResult(False, f"Scope '{scope}' has no allowed roots.", str(canonical))

    for root in allowed_roots:
        try:
            root_path = _canonicalize_path(root)
        except OSError:
            continue
        if _is_within(canonical, root_path):
            return ScopeValidationResult(True, "Filesystem scope allowed.", str(canonical))

    return ScopeValidationResult(False, "Path target is outside the allowed filesystem scope.", str(canonical))


def _allowed_values_for_scope(scope: str, session: ScopedSession) -> tuple[str, ...]:
    for grant in session.scope_grants:
        if grant.name == scope:
            return grant.values
    return ()


def _canonicalize_path(path: str) -> Path:
    candidate = Path(path).expanduser()
    if candidate.exists():
        return candidate.resolve(strict=True)
    if candidate.is_symlink():
        return candidate.resolve(strict=False)
    parent = candidate.parent if str(candidate.parent) else Path(".")
    return parent.resolve(strict=True) / candidate.name


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_protected_path(path: Path) -> bool:
    return any(_is_within(path, protected) or path == protected for protected in PROTECTED_PATHS)
