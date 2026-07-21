# NELA OS Roadmap

## Current Milestone

**M0: Collaboration Foundation**

Goal: Prepare the repository so multiple AI assistants can collaborate through GitHub without overwriting each other or losing project context.

## Milestones

### M0: Collaboration Foundation

- Create the top-level project structure.
- Add architecture documentation.
- Add AI handoff documentation.
- Add coding rules.
- Add assistant-specific prompt files.
- Define task traceability expectations.

### M1: Core Contracts

- Define shared interfaces in `core/`.
- Establish module boundaries.
- Add initial tests for shared contracts.
- Create configuration templates.

### M2: Agent Framework

- Define agent lifecycle concepts.
- Add agent registration patterns.
- Create examples for Codex, Claude, and ChatGPT collaboration through GitHub.
- Add tests for agent behavior.

### M3: Memory, Planner, And Skills

- Define memory interfaces.
- Define planning workflows.
- Create reusable skill structure.
- Add documentation for adding new skills.

### M4: Voice, Vision, Terminal, Browser

- Add module-specific contracts.
- Keep each capability isolated behind clear APIs.
- Add integration tests where practical.

### M5: Automation And Long-Term Operations

- Add automation workflows.
- Add release and maintenance scripts.
- Add operational documentation.
- Formalize review and handoff process.

## Task Traceability

Every task should have:

- A branch name.
- A short task ID or issue reference.
- A clear owner or acting AI assistant.
- Documentation updates when behavior changes.
- A handoff update before work stops.

Suggested task ID format:

```text
NELA-0001-short-description
```

