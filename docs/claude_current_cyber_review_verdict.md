# Claude Current Cyber Review Verdict

Date: 2026-07-27

Branch reviewed: `codex/nela-real-actions-cyber-learning`

Replacement bundle reviewed by Claude:
`nela-current-agent-code-review-c9b1cfa.zip`

## Summary

Claude reviewed the replacement bundle after the first bundle was found to be
missing support packages. The replacement bundle included `cyber_lab/`,
`memory/`, and `voice/`, allowing Claude to complete the evidence-based review
of the defensive cyber surface.

## Updated Verdict

Claude's final recommendation:

**APPROVE — ready to merge into `develop`**

## Findings

### F1 — cyber_lab source missing

Final status: **PASS**

Claude confirmed that `cyber_lab/` is defensive-only after reading the package.
The lab gate denies external targets, forbidden actions, missing authorization,
expired authorization, scope mismatches, and unapproved execution. It defaults
to dry-run behavior and requires owner-registered targets plus matching
time-boxed authorization before any allowed lab action.

Claude also confirmed that `cyber_lab/scanners.py` performs static analysis over
supplied text, produces defensive Sigma/YARA-style telemetry rules, and does not
perform shell execution, network fetching, scanning, or exploitation.

### F2 — isolate potentially blocking T0/T1 scans

Final status: **MEDIUM / non-blocking hardening**

Claude noted that `brain/dispatcher.py::_requires_isolation` isolates T2/T3 and
explicit isolation flags, but does not automatically isolate blocking T0/T1
scans. Filesystem-walking actions such as dependency scans could still hold the
runtime in-process.

Recommended fix:

- Mark long-running scanning capabilities with `isolate: true`, or
- Extend `_requires_isolation` to cover capabilities declared as
  filesystem-walking or long-running.

Recommended test:

- A T0/T1 scanning Agent that blocks past timeout should be terminated while the
  runtime remains responsive.

## Evidence Highlighted By Claude

- Security Agents do not use shell execution or outbound request libraries.
- `vulnerability_research` correlates supplied advisory data against local
  dependency files; it does not fetch CVEs from the network.
- `agents/policy.py` denies offensive intent and external targets before
  execution.
- R1 registry overwrite protection remains closed.
- K1 subprocess isolation and kill-switch wiring remain closed for T2/T3 and
  explicit isolation paths.
- Dispatcher authorization occurs before Agent execution.

## Next Task

Implement F2 isolation hardening for long-running or filesystem-walking T0/T1
security scans.
