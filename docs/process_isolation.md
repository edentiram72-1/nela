# Process Isolation Foundation

Status: wired into Dispatcher policy on `feature/NELA-safety-spine-routing`.

## Purpose

Python threads cannot reliably stop blocked or high-risk Agent work. Any Agent
task that can block indefinitely, carries T2/T3 risk, or is explicitly marked
for isolation must run behind a subprocess boundary before NELA claims forced
termination behavior.

## Current Foundation

`agents.process_isolation.IsolatedAgentProcessRunner` runs a callable in a child
process and returns a structured `ProcessExecutionResult`. `brain.dispatcher`
uses this runner for T2, T3, and explicitly isolated tasks.

Timeout and cancellation behavior:

1. Invoke the optional `before_terminate` hook.
2. Terminate the child process.
3. Escalate to kill if the child remains alive.
4. Return timeout, cancellation, crash, failed, unknown, or completed state
   without pretending that a thread was interrupted.

The Dispatcher hook revokes scoped sessions before terminating the process.

## Dispatcher Policy

The Dispatcher isolates:

- `T2` tasks.
- `T3` tasks.
- Tasks with `payload.requires_isolation` or `payload.isolate`.

The Dispatcher does not isolate simple proven non-blocking `T0`/`T1` tasks by
default. This keeps low-risk status and local helper operations lightweight.

## Current Limits

- There is no worker pool yet.
- There is no streamed output protocol yet.
- A dedicated runtime supervisor is still future work.

## Future Work

- Dedicated runtime supervisor.
- Per-Agent process policies.
- Resource limits.
- Structured event streaming from child processes.
- Durable audit flush before `T2` and `T3` execution.
