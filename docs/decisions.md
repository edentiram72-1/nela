# Architecture Decisions

This file records significant architecture and process decisions for NELA OS.

Use a new entry for every decision that changes module boundaries, project structure, collaboration rules, or long-term direction.

## Decision Template

```text
ID:
Date:
Status:
Context:
Decision:
Consequences:
Related files:
```

## Decisions

### DEC-0001: Use GitHub As The Multi-AI Collaboration Layer

**Date:** 2026-07-22  
**Status:** Accepted

**Context:** NELA OS needs to support collaboration between Codex, Claude, ChatGPT, and future AI assistants. Direct assistant-to-assistant communication would add complexity and fragility.

**Decision:** Use GitHub as the shared source of truth. Assistants collaborate through repository files, branches, commits, pull requests, issues, and `docs/ai_handoff.md`.

**Consequences:**

- Every assistant can clone the repository and understand the current state.
- Work is traceable through Git history and documentation.
- Merge conflicts are reduced by keeping modules independent.
- No direct communication channel with Claude is required.

**Related files:**

- `README.md`
- `docs/ai_handoff.md`
- `docs/coding_rules.md`

### DEC-0002: Keep Top-Level Modules Independent

**Date:** 2026-07-22  
**Status:** Accepted

**Context:** Multiple assistants may work on different features at the same time. Coupled modules increase the risk of merge conflicts and accidental regressions.

**Decision:** Use clear top-level folders for major capabilities and keep each feature inside the smallest relevant module.

**Consequences:**

- Assistants can work in separate folders with fewer conflicts.
- Shared abstractions must be deliberate and documented.
- Cross-module changes require extra review and handoff notes.

**Related files:**

- `docs/architecture.md`
- `docs/coding_rules.md`

