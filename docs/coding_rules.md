# Coding Rules

## Collaboration Rules

1. Use one feature or fix per branch.
2. Make small commits.
3. Update documentation with every meaningful feature.
4. Update `docs/ai_handoff.md` before stopping work.
5. Keep modules independent.
6. Never modify unrelated code.
7. Add tests whenever practical.
8. Record major structural changes in `docs/decisions.md`.
9. Use review bundles or GitHub pull requests for Claude collaboration; do not create a direct Claude connection.

## Branch Naming

Use clear branch names:

```text
feature/NELA-0001-core-contracts
fix/NELA-0002-terminal-error-handling
docs/NELA-0003-update-handoff
```

## Commit Style

Use short, specific commit messages:

```text
Add core contract placeholders
Document memory module API
Fix planner task ordering test
```

## Module Rules

- Put code in the most specific module folder.
- Do not move shared behavior into `core/` until at least two modules need it.
- Do not introduce circular dependencies.
- Do not rewrite completed modules without a documented reason.
- Prefer small interfaces over large shared abstractions.
- The Brain must not execute desktop, browser, file, service, or plugin actions directly.
- Agent-specific behavior belongs in Agents, not in `brain/`.
- Communication between major modules should happen through Events.
- New Agents must implement the shared contract in `agents/base.py`.

## Documentation Rules

Update documentation when:

- A new module is added.
- Public behavior changes.
- A new API or contract is introduced.
- Architecture changes.
- A known issue is discovered or resolved.
- Work is handed off to another AI assistant.

## Testing Rules

Add tests when practical for:

- Shared contracts.
- Data transformations.
- Automation.
- Planner behavior.
- Memory retrieval.
- Terminal and browser safety boundaries.
- Intent recognition.
- Decision logic.
- Context state.
- Agent dispatch behavior.

If tests are not added, explain why in `docs/ai_handoff.md`.

## AI-Specific Rules

### Codex

- Implement code.
- Fix bugs.
- Write tests.
- Refactor carefully.
- Never change architecture without documentation.

### Claude

- Review architecture.
- Suggest improvements.
- Review documentation.
- Find edge cases.
- Improve UX ideas.
- Never rewrite completed modules without justification.
- Review `docs/claude_review_bundle.md` or a GitHub pull request when local file access is not available.

### ChatGPT

- Define architecture.
- Design new systems.
- Coordinate development.
- Approve major structural changes.
