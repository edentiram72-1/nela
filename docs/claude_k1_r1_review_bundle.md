# NELA OS — K1/R1 Follow-Up Review Bundle

Branch: `codex/multi-agent-foundation-safety`

Code fix commit: `a1af5998d578a4ee164ed647104282bc94be968f`

Purpose: provide Claude with the refreshed implementation evidence for the two
remaining before-merge findings.

## Findings For Review

### K1 — Subprocess Isolation And Kill Switch

Relevant files:

- `brain/dispatcher.py`
- `agents/process_isolation.py`
- `permissions/engine.py`
- `tests/test_process_isolation.py`
- `tests/test_dispatcher.py`

Evidence to inspect:

- `AgentDispatcher._execute_agent`
- `AgentDispatcher._requires_isolation`
- `AgentDispatcher._agent_result_from_process`
- `IsolatedAgentProcessRunner`
- `PermissionEngine.revoke_all_scoped_sessions`

Expected behavior:

- T2/T3 work is routed through `IsolatedAgentProcessRunner`.
- Tasks may opt into isolation through `requires_isolation` or `isolate`.
- Timeout calls the revocation hook before terminating the child process.
- Process outcomes are converted back into `AgentResult` values.

### R1 — Agent Registry Overwrite Protection

Relevant files:

- `agents/registry.py`
- `tests/test_dispatcher.py`

Evidence to inspect:

- `AgentNotRegisteredError`
- `AgentRegistry.register`
- `AgentRegistry.replace`
- `AgentRegistry._store`
- `DispatcherTests.test_agent_replace_rejects_missing_agent`
- `DispatcherTests.test_agent_replace_requires_existing_agent`

Expected behavior:

- `register()` rejects duplicate Agent IDs.
- `replace()` rejects missing Agent IDs.
- Replacement succeeds only for an existing Agent ID.
- Rejected missing replacement attempts are recorded as `rejected_missing`.
- `_store()` requires each caller to declare whether the Agent must already
  exist.

## Validation

Executed after the R1 fix:

```text
python3 -m unittest tests.test_dispatcher
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
```

Result:

- Dispatcher focused tests passed: 12 tests.
- Full test suite passed: 120 tests.
- Hebrew language pack validation passed.
- UI headless smoke passed.

## Files Included In This Bundle

```text
docs/claude_k1_r1_review_prompt.md
docs/claude_k1_r1_review_bundle.md
agents/registry.py
brain/dispatcher.py
agents/process_isolation.py
permissions/engine.py
tests/test_dispatcher.py
tests/test_process_isolation.py
tests/test_permission_engine.py
```

## Notes

This bundle is intentionally small. It is not the stale Sprint 2 package. It is
the focused follow-up package for commit `a1af5998d578a4ee164ed647104282bc94be968f`.
