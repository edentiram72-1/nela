# AI Handoff

This file is the communication point between AI assistants working on NELA OS.

Every significant change must update this file before handoff.

## Current Project Status

The repository has been initialized with a collaboration-ready structure for multi-AI development through GitHub.

No application runtime has been implemented yet. The current work establishes folders, documentation, GitHub collaboration templates, role prompts, and development rules.

## Current Milestone

**M0: Collaboration Foundation**

## Active Branch

`main`

## Recently Modified Files

- `README.md`
- `.gitignore`
- `docs/architecture.md`
- `docs/roadmap.md`
- `docs/api.md`
- `docs/ai_handoff.md`
- `docs/decisions.md`
- `docs/coding_rules.md`
- `prompts/codex.md`
- `prompts/claude.md`
- `prompts/chatgpt.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.gitkeep` files in module folders

## Pending Tasks

- Create the first tracked issue or task ID for M1 core contracts.
- Define initial interfaces for `core/`.
- Decide the primary implementation language and package tooling.
- Add a test runner once a language stack is selected.
- Configure the remote GitHub repository when the destination repo is known.
- Create GitHub labels for feature, bug, docs, refactor, test, and architecture tasks.

## Known Issues

- No runtime code exists yet.
- No test tooling exists yet.
- No remote GitHub repository is configured locally.

## Suggested Next Task

Create task `NELA-0001-core-contracts` on a new branch and define the first shared contracts in `core/`.

## Notes For The Next AI Assistant

- Do not attempt to create a direct communication channel with Claude or any other assistant.
- Use GitHub as the collaboration layer.
- Read `docs/architecture.md` and `docs/coding_rules.md` before changing files.
- Keep each feature modular and isolated.
- Update this handoff file before stopping work.
- Record major structural decisions in `docs/decisions.md`.
