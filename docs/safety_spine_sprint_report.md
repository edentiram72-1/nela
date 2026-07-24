# Sprint 2 Safety Spine Sprint Report

Branch: `feature/NELA-safety-spine-routing`

Implementation review commit: `11a2991`

Required-fix commit: see final commit hash in handoff

Base branch: `develop`

## Goal

Sprint 2 establishes the Safety Spine for NELA OS. The central rule is that no
Agent execution should bypass the Permission Engine.

## Completed

- Permission Engine with T0-T4 tiers.
- Capability Registry and Agent manifests.
- Dispatcher authorization before Agent execution.
- Scoped authenticated sessions foundation.
- Confirmation binding to exact action tuple.
- Tamper-evident audit hash chain.
- Kill switch and lock mode.
- Event Bus subscriber isolation and bounded history.
- Secure local UI bridge foundation.
- Subprocess isolation foundation for future high-risk Agents.
- Dispatcher isolation policy for T2/T3 and explicitly isolated tasks.
- Kill Switch cancellation of blocked isolated workers.
- Protected Agent replacement with manifest fingerprint verification.
- Capability-first routing for Desktop Agent integration.

## Claude Review Verdict

Claude returned `APPROVE WITH REQUIRED FIXES` for PR #2. The before-merge fixes
were:

- K1: subprocess isolation existed but was not wired into Dispatcher execution.
- R1: Agent replacement could bypass duplicate-registration protection.

Both before-merge findings are fixed in the final required-fix commit.

## Non-Goals

- No merge into `develop`.
- No merge into `main`.
- No Coding Agent implementation.
- No Cyber Agent implementation.
- No Browser/Vision expansion.
- No UI redesign.
- No direct Claude communication channel.

## Validation

```text
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
```

Result:

- Language validation passed.
- 114 tests passed.
- UI headless smoke passed.

## Remaining Blockers

- Draft PR must still be created through GitHub web UI if automatic creation is
  unavailable.
- P1 stable identity enforcement is required before enabling
  `coding.files.write`, `files.write`, `files.move`, or `files.delete`.
- L1 durable default audit persistence, startup chain verification, and
  corruption fail-closed behavior are required before NELA 1.0 or durable T2/T3
  workflows.
- Task idempotency remains a required future safety item.
- Advanced Agents remain blocked until safety hardening is complete.
