"""Confirmation binding helpers.

Confirmations are bound to the exact action tuple they approve. A confirmation
for one Agent/action/target cannot be replayed for a different command.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any


IGNORED_PARAMETER_KEYS = {
    "confirmed",
    "confirmation_action_hash",
    "confirmation_expires_at",
    "task_id",
    "plan_id",
    "timeout_seconds",
}


def action_tuple_hash(
    *,
    agent: str | None,
    capability: str | None,
    action: str,
    target: str | None,
    parameters: dict[str, Any] | None = None,
    session: str | None = None,
    expires_at: datetime | None = None,
) -> str:
    payload = {
        "agent": agent,
        "capability": capability,
        "action": action,
        "target": target,
        "parameters": _stable_parameters(parameters or {}),
        "session": session,
        "expires_at": expires_at.astimezone(timezone.utc).isoformat() if expires_at else None,
    }
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _stable_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    return {
        key: parameters[key]
        for key in sorted(parameters)
        if key not in IGNORED_PARAMETER_KEYS
    }
