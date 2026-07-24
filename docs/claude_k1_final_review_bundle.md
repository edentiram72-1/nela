# Claude K1 Final Review Bundle

## Branch

codex/multi-agent-foundation-safety

## Commit

667c34cd07e2bc5722aaec35d2a830c95141ec52

## Purpose

This bundle addresses Claude's remaining K1 blocker from the previous review:
the kill switch blocked future authorization but did not terminate already
running isolated Agent work.

It also addresses Claude's follow-up concern that a terminated isolated attempt
could be retried without re-authorization while the kill switch is active.
The latest commit also closes the post-authorization race where the kill switch
becomes active after authorization but before an attempt starts.
The final commit closes the runner-registration race by re-checking emergency
state after runner registration and before starting the child process.

## Changes Since Previous Bundle

- Added `ProcessOutcome.TERMINATED`.
- Added `IsolatedAgentProcessRunner.terminate()` so a live child process can be stopped externally.
- Added `IsolatedProcessSupervisor` to track live isolated runners.
- Connected `PermissionEngine.activate_kill_switch()` to terminate tracked isolated runners after scoped sessions are revoked.
- Registered each isolated runner in `AgentDispatcher._execute_agent()` before execution and unregistered it in a `finally` block.
- Added a dispatcher regression test proving a running T2 isolated task is terminated when the kill switch fires mid-execution.
- Blocked retries after the kill switch is active for any non-T0 permission boundary.
- Added a dispatcher regression test proving a two-attempt T2 task records only one child-process start after kill-switch termination.
- Added a pre-attempt emergency stop check so kill switch or lock mode activation after authorization prevents first-attempt execution.
- Added a dispatcher regression test proving a post-authorization kill switch prevents the Agent from writing its marker before execution.
- Added a post-runner-registration emergency stop check so a kill switch activated after runner registration prevents child process start.
- Added a dispatcher regression test proving a runner-registration kill switch prevents the Agent from writing its marker.

## Security Behavior

The new kill switch flow is:

1. Set `kill_switch_active = True`.
2. Revoke all scoped sessions.
3. Terminate all live isolated runners.
4. Publish `KillSwitchActivated` with:
   - `revoked_sessions`
   - `terminated_processes`

This means the kill switch now affects both:

- future non-T0 authorization attempts
- in-flight isolated T2/T3 work
- retry behavior after an isolated process is terminated
- the race window between authorization and execution start
- the race window between runner registration and child process start

## Files Changed In Commit

- `agents/process_isolation.py`
- `permissions/engine.py`
- `brain/dispatcher.py`
- `tests/test_dispatcher.py`

## Included Supporting Files For Reproducibility

The ZIP also includes supporting files that were missing from the previous bundle and are needed for dispatcher/permission tests:

- `agents/base.py`
- `agents/registry.py`
- `brain/planner.py`
- `core/events.py`
- `permissions/__init__.py`
- `permissions/audit.py`
- `permissions/confirmation.py`
- `permissions/models.py`
- `permissions/registry.py`
- `permissions/scope.py`
- `tests/test_process_isolation.py`
- `tests/test_permission_engine.py`

## Local Validation

```text
python3 -m unittest discover -s tests
124 tests passed

python3 -m scripts.validate_language_packs
passed

python3 -m ui.app --headless-smoke
passed
```

## Remaining Known Limitation

The current isolated process termination is a local runtime foundation. It is not yet a full async orchestration service. Future multi-agent orchestration can replace the supervisor internals without changing the dispatcher contract.
