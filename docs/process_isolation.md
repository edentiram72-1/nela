# Process Isolation Foundation

Status: implemented foundation on `feature/NELA-safety-spine-routing`.

## Purpose

Python threads cannot reliably stop blocked or high-risk Agent work. Any future
Agent that can block indefinitely or perform high-risk execution must run behind
a subprocess boundary before NELA claims forced termination behavior.

## Current Foundation

`agents.process_isolation.IsolatedAgentProcessRunner` runs a callable in a child
process and returns a structured `ProcessExecutionResult`.

Timeout behavior:

1. Invoke the optional `before_terminate` hook.
2. Terminate the child process.
3. Escalate to kill if the child remains alive.
4. Return a timeout result without pretending that a thread was interrupted.

The hook is intended for actions such as scoped-session revocation before
terminating the process.

## Current Limits

- Existing safe MVP Agents are not moved into subprocesses in Sprint 2.
- There is no worker pool yet.
- There is no streamed output protocol yet.
- High-risk Agent enablement remains blocked until this runtime boundary is
  connected to the Agent lifecycle.

## Future Work

- Dedicated runtime supervisor.
- Per-Agent process policies.
- Resource limits.
- Structured event streaming from child processes.
- Durable audit flush before `T2` and `T3` execution.
