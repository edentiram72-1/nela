"""Policy-enforced local cyber lab facade."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse

from cyber_lab.models import (
    AuthorizationScopeType,
    CyberAuthorization,
    CyberLabActionRequest,
    CyberLabAuditRecord,
    CyberLabDecision,
    CyberLabDecisionType,
    CyberLabTarget,
    FORBIDDEN_ACTIONS,
)


class CyberLab:
    """Small in-memory cyber lab control plane.

    This does not perform network scanning or exploitation. It validates and
    records whether an action could be handed to a future sandboxed runner.
    """

    def __init__(self) -> None:
        self._targets: dict[str, CyberLabTarget] = {}
        self._audit: list[CyberLabAuditRecord] = []
        self.kill_switch_active = False

    def add_target(self, target: CyberLabTarget) -> None:
        self._targets[target.identifier] = target

    def target_allowlist(self) -> tuple[str, ...]:
        return tuple(sorted(self._targets))

    def audit_log(self) -> tuple[CyberLabAuditRecord, ...]:
        return tuple(self._audit)

    def activate_kill_switch(self, reason: str = "manual") -> CyberLabDecision:
        self.kill_switch_active = True
        return self._record(
            action="kill_switch.activate",
            target=None,
            request_id="kill-switch",
            authorization_id=None,
            dry_run=False,
            decision=CyberLabDecisionType.KILL_SWITCH_ACTIVE,
            reason=f"Cyber lab kill switch activated: {reason}",
        )

    def deactivate_kill_switch(self, reason: str = "manual") -> CyberLabDecision:
        self.kill_switch_active = False
        return self._record(
            action="kill_switch.deactivate",
            target=None,
            request_id="kill-switch",
            authorization_id=None,
            dry_run=False,
            decision=CyberLabDecisionType.ALLOWED,
            reason=f"Cyber lab kill switch deactivated: {reason}",
        )

    def evaluate(self, request: CyberLabActionRequest) -> CyberLabDecision:
        auth = request.authorization
        if self.kill_switch_active:
            return self._record_request(request, CyberLabDecisionType.KILL_SWITCH_ACTIVE, "Kill switch is active.")
        if _looks_external(request.target):
            return self._record_request(request, CyberLabDecisionType.DENIED, "External targets are not allowed.")
        if auth is None:
            return self._record_request(request, CyberLabDecisionType.APPROVAL_REQUIRED, "Missing cyber authorization.")
        if not auth.is_active():
            return self._record_request(request, CyberLabDecisionType.DENIED, "Cyber authorization is expired.")
        forbidden = set(auth.forbidden_actions)
        if request.action in FORBIDDEN_ACTIONS or request.action in forbidden:
            return self._record_request(request, CyberLabDecisionType.DENIED, "Requested action is forbidden.")
        if set(auth.allowed_actions) & FORBIDDEN_ACTIONS:
            return self._record_request(request, CyberLabDecisionType.DENIED, "Authorization cannot approve forbidden action classes.")
        if request.action not in auth.allowed_actions:
            return self._record_request(request, CyberLabDecisionType.DENIED, "Action is not approved by authorization.")
        if request.target not in auth.targets:
            return self._record_request(request, CyberLabDecisionType.DENIED, "Target is outside the authorization target list.")
        target = self._targets.get(request.target)
        if target is None:
            return self._record_request(request, CyberLabDecisionType.DENIED, "Target is not in the local allowlist.")
        if target.scope_type != auth.scope_type:
            return self._record_request(request, CyberLabDecisionType.DENIED, "Target scope type does not match authorization.")
        if auth.scope_type not in set(AuthorizationScopeType):
            return self._record_request(request, CyberLabDecisionType.DENIED, "Unsupported cyber authorization scope.")
        if not request.approved:
            return self._record_request(request, CyberLabDecisionType.APPROVAL_REQUIRED, "Explicit approval gate is required.")
        if request.dry_run:
            return self._record_request(request, CyberLabDecisionType.DRY_RUN_ONLY, "Dry-run approved; no active step executed.")
        return self._record_request(request, CyberLabDecisionType.ALLOWED, "Action approved for isolated lab runner.")

    def _record_request(
        self,
        request: CyberLabActionRequest,
        decision: CyberLabDecisionType,
        reason: str,
    ) -> CyberLabDecision:
        return self._record(
            action=request.action,
            target=request.target,
            request_id=request.id,
            authorization_id=request.authorization.id if request.authorization else None,
            dry_run=request.dry_run,
            decision=decision,
            reason=reason,
        )

    def _record(
        self,
        action: str,
        target: str | None,
        request_id: str,
        authorization_id: str | None,
        dry_run: bool,
        decision: CyberLabDecisionType,
        reason: str,
    ) -> CyberLabDecision:
        record = CyberLabAuditRecord(
            action=action,
            target=target,
            decision=decision,
            reason=reason,
            dry_run=dry_run,
            authorization_id=authorization_id,
            request_id=request_id,
        )
        self._audit.append(record)
        return CyberLabDecision(
            decision=decision,
            reason=reason,
            request_id=request_id,
            audit_id=record.id,
            dry_run=dry_run,
            target=target,
        )


def _looks_external(target: str) -> bool:
    parsed = urlparse(target)
    if parsed.scheme in {"http", "https", "ssh", "tcp"}:
        host = parsed.hostname
        if host is None:
            return True
        return not _is_local_or_private_host(host)
    try:
        address = ipaddress.ip_address(target)
    except ValueError:
        return False
    return not (address.is_loopback or address.is_private)


def _is_local_or_private_host(host: str) -> bool:
    normalized = host.lower().strip("[]")
    if normalized in {"localhost", "127.0.0.1", "::1"} or normalized.endswith(".local"):
        return True
    try:
        address = ipaddress.ip_address(normalized)
    except ValueError:
        try:
            address = ipaddress.ip_address(socket.gethostbyname(normalized))
        except OSError:
            return False
    return address.is_loopback or address.is_private
