# Manual Draft PR Instructions

Automatic PR creation may be unavailable because GitHub CLI (`gh`) is not
installed/authenticated in the local shell and the GitHub connector may not have
permission to create pull requests.

Current branch: `feature/NELA-safety-spine-routing`

Current commit for review setup: `11a2991`

## Compare URL

Open this URL:

```text
https://github.com/edentiram72-1/nela/compare/develop...feature/NELA-safety-spine-routing?expand=1
```

## Branches

- Base / merge target: `develop`
- Head / source branch: `feature/NELA-safety-spine-routing`

Do not merge into `develop` or `main` yet.

## PR Title

```text
NELA Sprint 2 — Safety Spine and Intelligent Agent Routing
```

## PR Description

```markdown
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

## Validation

- Language validation passed
- UI headless smoke passed
- 114 tests passed

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

Do not merge yet.
```

## Checklist

- [ ] Confirm base branch is `develop`.
- [ ] Confirm head branch is `feature/NELA-safety-spine-routing`.
- [ ] Select **Create draft pull request**.
- [ ] Paste the PR title above.
- [ ] Paste the PR description above.
- [ ] Use the dropdown next to the submit button if needed and choose the draft
      pull request option.
- [ ] Create the PR as Draft.
- [ ] Send the PR link to Claude for review.
- [ ] Do not merge until Claude/Codex review is complete.
