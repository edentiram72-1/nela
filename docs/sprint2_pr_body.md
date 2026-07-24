## Summary

Implements Sprint 2 for NELA OS:

- Permission Engine with T0-T4
- Capability Registry
- Agent manifests
- Scoped authenticated sessions
- Confirmation binding
- Tamper-evident audit log
- Kill switch
- Lock mode
- Event Bus hardening
- Safer capability routing
- Desktop Agent permission integration

## Claude Required Fixes

Claude reviewed PR #2 and returned `APPROVE WITH REQUIRED FIXES`.

This update fixes the two before-merge blockers:

- K1: Dispatcher now routes T2/T3 and explicitly isolated tasks through
  `IsolatedAgentProcessRunner`; Kill Switch cancels blocked isolated workers,
  terminates the child process, revokes scoped sessions, and records failure in
  audit.
- R1: Agent replacement now requires explicit manifest-bound
  `ReplacementAuthorization`; missing replacement targets, self-replacement,
  manifest identity mismatch, version mismatch, and fingerprint mismatch fail.

## Validation

- Language validation passed
- UI headless smoke passed
- 114 tests passed
- Dedicated K1/R1 tests passed (38 tests)

## Security Review Requested

Claude findings to verify:

- A1 - WebView bridge authentication
- K1 - subprocess isolation and kill switch
- P1 - TOCTOU protection
- P2 - confirmation binding
- R1 - Agent Registry overwrite protection
- L1 - audit hash-chain integrity
- T1 - authorization-safe routing
- T2 - prompt-injection-resistant routing

## Status

Draft review only.

Do not merge until Claude re-reviews the required-fix commit.
