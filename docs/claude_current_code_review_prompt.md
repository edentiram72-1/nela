# NELA OS — Current Code Review Request

This bundle is for Claude review through the GitHub / attached-file workflow.
It does not create any direct AI-to-AI connection.

## Current Branch

`codex/nela-real-actions-cyber-learning`

## Current Commit

`6196dd4fd5b678115ce8d75b5da938ba96d5f000`

## Review Goal

Review the actual current implementation, not earlier chat summaries or stale
fragments. The bundle includes the full Agent code and the supporting Brain,
Permission, Language, UI, and test files needed to evaluate the defensive cyber
and learning work.

## Please Review

1. Whether the defensive cyber Agents remain passive, local, authorized, and
   non-offensive.
2. Whether security actions emit useful findings, remediation, severity, and
   safe next steps.
3. Whether `brain/dispatcher.py` enforces permission checks before execution.
4. Whether the Permission Engine, Capability Registry, scoped sessions, audit
   log, kill switch, and lock mode are still respected by the new Agent routes.
5. Whether R1 and K1 remain closed in the current code:
   - R1: Agent registration/replacement must not silently overwrite Agents.
   - K1: isolated/high-risk work must be terminable and must not continue after
     kill switch or lock mode activation.
6. Whether Hebrew routing and Language Engine responses make NELA behave more
   like a useful assistant rather than only describing capabilities.
7. Remaining blockers before a pull request to `develop`.

## Safety Bar

- No external target scanning unless a future explicit lab/owned-scope flow is
  implemented and authorized.
- No exploit payloads, persistence, credential theft, phishing, evasion, DDoS,
  or malware behavior.
- Local scans must stay read-only and redact likely secrets.
- Refusals should be audited as clearly as allowed actions.

## Expected Output

Return:

- PASS / PARTIAL / FAIL table for R1, K1, defensive-only cyber behavior, routing
  order, permission enforcement, auditability, and UI bridge safety.
- Ship-blocking findings first.
- File-specific evidence.
- Recommended next tasks in priority order.
