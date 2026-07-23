# Agents Module

## Purpose

Agents are independent capability executors. The Brain delegates tasks to Agents; Agents execute work and report status.

## Responsibilities

- Expose a consistent lifecycle.
- Execute assigned tasks.
- Report status and health.
- Avoid direct dependencies on other Agents.

## Public API

Every Agent must expose:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

Shared types:

- `BaseAgent`
- `AgentCommand`
- `AgentResult`
- `AgentState`
- `AgentRegistry`

## Current Agents

- `terminal`
- `browser`
- `spotify`
- `files`
- `calendar`
- `gmail`
- `github`
- `claude`
- `codex`
- `automation`
- `vision`
- `desktop`

## Known Limitations

- Current Agents are placeholders.
- Real external integrations are not implemented yet.
- The Claude Agent intentionally does not connect to Claude directly. It only prepares review requests and Markdown bundles.

## Future Improvements

- Capability manifests.
- Permission policies.
- Agent sandboxing.
- Plugin-backed dynamic loading.
- Integration tests for critical Agents.
