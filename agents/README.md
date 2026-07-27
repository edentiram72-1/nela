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
- `automation_workflow`
- `computer_control`
- `app_automation`
- `file_automation`
- `process_automation`
- `scheduler_automation`
- `vision`
- `desktop`
- `orchestrator`
- `planner`
- `memory`
- `learning`
- `quality_self_evaluation`
- `code_architect`
- `backend`
- `frontend`
- `mobile`
- `devops`
- `code_reviewer`
- `test_qa`
- `test_engineer`
- `documentation`
- `llm_engineer`
- `ml_engineer`
- `data_engineer`
- `research`
- `documentation_researcher`
- `trend_monitor`
- `security_researcher`
- `secure_code_reviewer`
- `vulnerability_research`
- `infrastructure_security`
- `threat_intelligence`
- `sentinel`
- `incident_commander`
- `containment`
- `deception`
- `forensics`
- `threat_hunter`
- `red_team_simulator`
- `blue_team`
- `purple_team`
- `exploit_validation`
- `detection_engineering`
- `recovery`
- `anomaly_discovery`
- `authorized_lab`

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
- Sigma/YARA detection scaffold generation.
- Incident triage, containment planning, forensics, recovery, and purple-team
  gap analysis inside owned scope.

They must not build or assist with exploitation, persistence, credential theft,
evasion, malware, phishing, DDoS, or attacks against external targets.
Active cyber actions require authorization, target allowlist, scoped session,
confirmation, audit logging, and Cyber Lab dry-run/kill-switch controls.
`authorized_lab` is the first control-plane Agent for that flow. It registers
local/lab targets, evaluates scoped authorizations, records audit decisions, and
prepares dry-run scans or local fuzz cases without contacting external systems.

## Computer Automation

The automation layer is split into narrow local specialists:

- `automation`: routes computer tasks and creates high-level workflows.
- `automation_workflow`: creates and validates repeatable runbooks.
- `computer_control`: plans keyboard, mouse, and screen sequences in dry-run form.
- `app_automation`: plans application lifecycle workflows for handoff to Desktop Agent.
- `file_automation`: previews file operations and flags unsafe paths.
- `process_automation`: previews and runs a tiny allowlist of local verification commands without shell access.
- `scheduler_automation`: plans recurring local tasks without installing persistent timers.

`process_automation.run_allowlisted_command` is intentionally narrow. It
supports only known local verification commands, defaults to dry-run, requires
`approved=True` for real execution, and is declared as T2 so Dispatcher routing
requires confirmation before it runs.

Sandbox profiles are declarative for now. Each specialist manifest includes a
`permission_profile` with allowed tools, filesystem scope, network access, and
process execution limits. Future runtime integrations should enforce those
profiles before any side-effecting tool is attached.

## Known Limitations

- Some tool-facing Agents are placeholders, but the automation coordinator,
  runbook, UI-plan, app-plan, file-preview, process, and scheduler automation
  agents now return structured work products.
- Real external integrations are not implemented yet.
- The Claude Agent intentionally does not connect to Claude directly. It only prepares review requests and Markdown bundles.
- Security analysis is local and heuristic. It is a defensive aid, not a release
  gate by itself.

## Future Improvements

- Runtime enforcement for every declarative sandbox profile.
- Plugin-backed dynamic loading.
- Integration tests for critical Agents.
