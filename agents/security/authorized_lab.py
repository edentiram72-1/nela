"""Authorized local cyber-lab agent."""

from __future__ import annotations

from agents.base import AgentCommand
from agents.foundation import SpecialistAgent, artifact
from agents.task_schema import AgentDomain, AgentWorkProduct, RiskLevel, TaskFinding
from cyber_lab import (
    AuthorizationScopeType,
    CyberAuthorization,
    CyberLab,
    CyberLabActionRequest,
    CyberLabDecisionType,
    CyberLabTarget,
    audit_config_text,
    build_local_fuzz_cases,
    scan_source_text,
)
from cyber_lab.models import FORBIDDEN_ACTIONS


class AuthorizedLabAgent(SpecialistAgent):
    name = "authorized_lab"
    domain = AgentDomain.SECURITY
    purpose = "Gate local/owned cyber-lab checks through authorization, dry-run, allowlists, and audit records."
    capabilities = ("authorized_lab.target", "authorized_lab.evaluate", "authorized_lab.scan", "authorized_lab.fuzz")

    def __init__(self, lab: CyberLab | None = None) -> None:
        super().__init__()
        self.lab = lab or CyberLab()

    def _handlers(self):
        return {
            **super()._handlers(),
            "register_lab_target": self._register_lab_target,
            "evaluate_lab_action": self._evaluate_lab_action,
            "scan_lab_target": self._scan_lab_target,
            "run_local_fuzzing": self._run_local_fuzzing,
            "lab_status": self._lab_status,
            "activate_lab_kill_switch": self._activate_lab_kill_switch,
            "deactivate_lab_kill_switch": self._deactivate_lab_kill_switch,
        }

    def _register_lab_target(self, command: AgentCommand) -> AgentWorkProduct:
        target = _target_from_payload(command.payload)
        self.lab.add_target(target)
        return AgentWorkProduct(
            summary="Authorized lab target registered.",
            artifacts=(
                artifact(
                    "lab_target",
                    "registered_lab_target",
                    (
                        f"target={target.identifier}",
                        f"scope_type={target.scope_type.value}",
                        f"owner={target.owner}",
                        f"proof={target.proof}",
                    ),
                ),
            ),
            next_steps=("Submit a CyberAuthorization before scan_lab_target or run_local_fuzzing.",),
        )

    def _evaluate_lab_action(self, command: AgentCommand) -> AgentWorkProduct:
        request = _request_from_payload(command.action, command.payload)
        decision = self.lab.evaluate(request)
        return AgentWorkProduct(
            summary=f"Cyber-lab action evaluated: {decision.decision.value}.",
            artifacts=(artifact("audit", "lab_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),),
        )

    def _scan_lab_target(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.evaluate(_request_from_payload("scan_lab_target", command.payload))
        if not decision.allowed:
            return _decision_product(decision)

        findings = []
        for path, source in _files_from_payload(command.payload).items():
            findings.extend(_finding_from_scanner(item, "sast") for item in scan_source_text(source, path=path))
        config = str(command.payload.get("config", ""))
        findings.extend(_finding_from_scanner(item, "config_audit") for item in audit_config_text(config))
        return AgentWorkProduct(
            summary=f"Authorized lab scan prepared for {decision.target}.",
            findings=tuple(findings),
            artifacts=(artifact("audit", "lab_scan_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),),
            next_steps=(
                "Apply fixes locally, then rerun the same scan.",
                "Keep active testing inside the approved target and time window.",
            ),
        )

    def _run_local_fuzzing(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.evaluate(_request_from_payload("run_local_fuzzing", command.payload))
        if not decision.allowed:
            return _decision_product(decision)

        input_types = command.payload.get("input_types")
        selected = tuple(str(item) for item in input_types) if isinstance(input_types, (list, tuple)) else None
        cases = build_local_fuzz_cases(selected)
        return AgentWorkProduct(
            summary=f"Local fuzzing dry-run prepared for {decision.target}.",
            artifacts=(
                artifact("audit", "lab_fuzz_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),
                artifact("fuzz_cases", "local_fuzz_cases", tuple(repr(case) for case in cases)),
            ),
            next_steps=("Wire these cases into local tests or a sandboxed harness before increasing volume.",),
        )

    def _lab_status(self, command: AgentCommand) -> AgentWorkProduct:
        return AgentWorkProduct(
            summary=f"Cyber lab has {len(self.lab.target_allowlist())} target(s) and {len(self.lab.audit_log())} audit record(s).",
            artifacts=(
                artifact("targets", "lab_targets", self.lab.target_allowlist() or ("No registered targets.",)),
                artifact("audit", "lab_audit", tuple(str(record.to_dict()) for record in self.lab.audit_log()) or ("No audit records.",)),
            ),
        )

    def _activate_lab_kill_switch(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.activate_kill_switch(str(command.payload.get("reason", "manual")))
        return _decision_product(decision)

    def _deactivate_lab_kill_switch(self, command: AgentCommand) -> AgentWorkProduct:
        decision = self.lab.deactivate_kill_switch(str(command.payload.get("reason", "manual")))
        return _decision_product(decision)


def _target_from_payload(payload: dict[str, object]) -> CyberLabTarget:
    scope_type = AuthorizationScopeType(str(payload.get("scope_type", AuthorizationScopeType.LOCAL_LAB.value)))
    identifier = str(payload.get("target", payload.get("identifier", "localhost")))
    return CyberLabTarget(
        identifier=identifier,
        scope_type=scope_type,
        owner=str(payload.get("owner", "local-owner")),
        proof=str(payload.get("proof", "declared-owned-local-lab")),
        metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), dict) else {},
    )


def _request_from_payload(action: str, payload: dict[str, object]) -> CyberLabActionRequest:
    requested_action = str(payload.get("action", action))
    authorization_payload = payload.get("authorization")
    authorization = _authorization_from_payload(authorization_payload) if isinstance(authorization_payload, dict) else None
    return CyberLabActionRequest(
        action=requested_action,
        target=str(payload.get("target", "")),
        authorization=authorization,
        dry_run=bool(payload.get("dry_run", True)),
        approved=bool(payload.get("approved", False)),
        metadata=dict(payload.get("metadata", {})) if isinstance(payload.get("metadata"), dict) else {},
    )


def _authorization_from_payload(payload: dict[str, object]) -> CyberAuthorization:
    forbidden_actions = payload.get("forbidden_actions")
    return CyberAuthorization(
        owner=str(payload.get("owner", "local-owner")),
        scope_type=AuthorizationScopeType(str(payload.get("scope_type", AuthorizationScopeType.LOCAL_LAB.value))),
        targets=tuple(str(item) for item in payload.get("targets", ())),
        allowed_actions=tuple(str(item) for item in payload.get("allowed_actions", ())),
        forbidden_actions=tuple(str(item) for item in forbidden_actions) if forbidden_actions is not None else tuple(sorted(FORBIDDEN_ACTIONS)),
        approved_by=str(payload.get("approved_by", "local-owner")),
    )


def _files_from_payload(payload: dict[str, object]) -> dict[str, str]:
    files = payload.get("files")
    if isinstance(files, dict):
        return {str(path): str(source) for path, source in files.items()}
    source = str(payload.get("source", ""))
    return {"inline": source} if source else {}


def _finding_from_scanner(item: dict[str, str], category: str) -> TaskFinding:
    return TaskFinding(
        title=item.get("title", "Finding"),
        severity=_risk_level(item.get("severity", "info")),
        category=category,
        location=item.get("location"),
        evidence=item.get("evidence"),
        recommendation=item.get("recommendation"),
    )


def _risk_level(value: object) -> RiskLevel:
    try:
        return RiskLevel(str(value).lower())
    except ValueError:
        return RiskLevel.INFO


def _decision_product(decision) -> AgentWorkProduct:
    severity = RiskLevel.INFO if decision.decision in {CyberLabDecisionType.ALLOWED, CyberLabDecisionType.DRY_RUN_ONLY} else RiskLevel.HIGH
    return AgentWorkProduct(
        summary=f"Cyber-lab action {decision.decision.value}: {decision.reason}",
        findings=(
            TaskFinding(
                title=f"Cyber-lab decision: {decision.decision.value}",
                severity=severity,
                category="authorized_lab",
                location=decision.target,
                evidence=decision.audit_id,
                recommendation="Adjust authorization, target allowlist, approval, or scope before retrying.",
            ),
        ),
        artifacts=(artifact("audit", "lab_decision", tuple(f"{key}={value}" for key, value in decision.to_dict().items())),),
    )
