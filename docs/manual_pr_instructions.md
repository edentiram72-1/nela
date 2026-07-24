# Manual Draft PR Instructions

Automatic PR creation was not available because GitHub CLI (`gh`) is not
installed/authenticated in the local shell.

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

Implements the first production Safety Spine for NELA OS.

### Included

- Permission Engine
- Capability Registry
- Agent Manifests
- Scoped Sessions
- Authentication foundation
- Audit Log
- Kill Switch
- Lock Mode
- Event Bus hardening
- Intelligent capability routing
- Desktop Agent integration

### Validation

- Language validation passed
- UI headless smoke passed
- 100 tests passed

### Review Requested

Please review:

- A1
- K1
- P1
- P2
- R1
- L1
- T1
- T2

No merge requested yet.
```

## Checklist

- [ ] Confirm base branch is `develop`.
- [ ] Confirm head branch is `feature/NELA-safety-spine-routing`.
- [ ] Select **Create draft pull request**.
- [ ] Paste the PR title above.
- [ ] Paste the PR description above.
- [ ] Create the PR as Draft.
- [ ] Send the PR link to Claude for review.
- [ ] Do not merge until Claude/Codex review is complete.
