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
- `orchestrator`
- `planner`
- `learning`
- `code_architect`
- `backend`
- `frontend`
- `test_qa`
- `secure_code_reviewer`
- `vulnerability_research`
- `anomaly_discovery`

## Multi-Agent Foundation

The first specialist layer is registered with:

```python
from agents import build_default_registry

registry = build_default_registry()
```

The specialist agents expose manifests through `AgentRegistry.manifests()` and use
the shared schema in `agents/task_schema.py`:

- `AgentTask`
- `TaskFinding`
- `TaskArtifact`
- `AgentWorkProduct`

The policy guard in `agents/policy.py` keeps security work defensive and
authorized. Security agents may help with:

- SAST-style code review.
- Dependency scanning.
- Config auditing.
- Local/lab fuzzing plans.
- Anomaly detection.
- Threat modeling.
- CVE/advisory correlation from approved input data.

They must not build or assist with exploitation, persistence, credential theft,
evasion, malware, phishing, DDoS, or attacks against external targets.

Sandbox profiles are declarative for now. Each specialist manifest includes a
`permission_profile` with allowed tools, filesystem scope, network access, and
process execution limits. Future runtime integrations should enforce those
profiles before any side-effecting tool is attached.

## Known Limitations

- Current Agents are placeholders.
- Real external integrations are not implemented yet.
- The Claude Agent intentionally does not connect to Claude directly. It only prepares review requests and Markdown bundles.
- Security analysis is local and heuristic. It is a defensive aid, not a release
  gate by itself.

## Future Improvements

- Capability manifests.
- Permission policies.
- Agent sandboxing.
- Plugin-backed dynamic loading.
- Integration tests for critical Agents.
