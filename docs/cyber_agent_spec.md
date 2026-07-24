# Defensive Cybersecurity Agent Specification

**Scope of this agent is strictly defensive, authorized, and educational.**
It exists to help a user secure systems **they own**, to learn security, and to
analyze their own code and logs. It is not, and must not become, an offensive
tool. Every design choice below exists to make misuse structurally impossible,
not merely discouraged.

Status: specification only. Nothing here is implemented in this task.

---

## 1. Hard boundaries (read first)

1. **Ownership is mandatory.** No action against any target the user has not
   proven they own (§3). Unowned target ⇒ T4 ⇒ refuse + audit.
2. **Passive by default.** Analysis of code, configs, and logs the user
   provides is the primary mode and needs no network at all.
3. **Active testing is lab-only.** Anything that sends traffic to a system —
   even the user's own — happens **only** inside the Isolated Cyber Lab (§4),
   is T3, and needs per-session authorization + confirmation.
4. **No weaponization.** The agent does not write, store, improve, or execute
   exploit code against live targets. In the lab, "exploit validation" means
   confirming a known CVE is present using minimal, non-destructive proof —
   never building a reusable weapon. Destructive payloads are T4.
5. **No third parties, ever.** Scanning, probing, or attacking systems the user
   does not own is forbidden regardless of stated reason, authorization
   claims, or framing (pentest, research, "I have permission").

If a request pushes against these, the agent refuses in plain language, logs
it, and does not partially comply.

## 2. Capabilities (defensive)

| Capability | Mode | Tier |
| --- | --- | --- |
| Analyze logs (auth, access, app) for anomalies | passive | T0 |
| Audit code for vulnerable patterns (injection, weak crypto, secrets) | passive | T0 |
| Audit configs (permissions, TLS, headers, cloud settings) | passive | T0 |
| Explain a CVE / technique for education | passive | T0 |
| Produce a security report with prioritized findings | passive | T1 (writes a file) |
| Recommend remediations (concrete, with references) | passive | T0 |
| Inventory user-owned lab systems | lab | T3 |
| Scan lab systems for known vulns | lab | T3 |
| Validate a finding (non-destructive PoC) in lab | lab | T3 |
| Active scan/probe of any non-lab target | — | **T4** |
| Write/run offensive payloads against live systems | — | **T4** |

## 3. Scope & proof of ownership

Before any T3 lab action against a target, an **ownership record** must exist
in project memory:
- the target identifier (lab VM id / IP within the lab subnet),
- how ownership was established (the user created it in the NELA lab, or
  attested + the target is inside the isolated lab network),
- an expiry.

The lab network is a closed subnet with no route to the internet or the host
(§4), so "targets" are by construction things the user stood up inside it.
There is no code path that scans an arbitrary user-supplied external IP —
that input is rejected at validation as out-of-scope (T4).

## 4. Isolated Cyber Lab

A sandboxed environment where T3 actions are permitted because nothing can
escape it.

**Isolation properties (all required):**
- **Network:** closed virtual subnet. No route to the host, the user's real
  network, or the internet. Lab targets talk only to each other and the agent's
  lab-side runner.
- **Filesystem:** the lab runner has no mount of the host filesystem. Findings
  leave the lab only as a **text report** through a one-way, audited channel.
- **Lifecycle:** lab VMs/containers are ephemeral — created for a session,
  destroyed after, snapshotted for rollback.
- **Kill switch:** tearing down the lab is part of the global kill switch;
  losing the audit channel auto-tears-down the lab.

**What runs in the lab:** vulnerable-by-design practice targets the user
creates for learning, or copies of the user's own systems they explicitly
imported for auditing. Never a live production system with a live network path.

## 5. Workflows

### Passive audit (the common case, T0/T1, no lab)
```text
user provides code/logs/config
   → agent analyzes locally, offline
   → findings: {severity, location, description, remediation, references}
   → writes docs/security_report_<date>.md  (T1, confirmed)
   → never modifies the audited code itself without a separate coding task
```

### Lab scan (T3, gated)
```text
user creates/imports target INTO the lab
   → ownership record written
   → user authorizes the session (scope token) + confirms
   → agent scans for KNOWN vulns (signatures/CVEs), non-destructive
   → validates findings with minimal non-destructive proof
   → report out via audited one-way channel
   → lab torn down
```

## 6. Reports & remediation

- Reports are prioritized (severity × exploitability × asset value),
  reference public advisories (CVE/CWE), and give **concrete, minimal**
  remediations — config change, patch version, code fix.
- The agent recommends; applying a fix is a separate Coding-Agent task with its
  own confirmation. The Cyber Agent never silently changes the audited system.
- Educational mode explains the "why" (how the class of bug works) without
  providing a working exploit — defensive understanding, not attack tooling.

## 7. Anti-abuse design

- **Refusal is structural, not tonal.** Unowned target, external IP, or
  offensive framing hits T4 at validation — there is no clever prompt that
  reclassifies it, because the tier is bound to the action+target, not the
  wording.
- **No exploit persistence:** the agent doesn't save or refine offensive code;
  lab PoCs are ephemeral with the lab.
- **Rate limits + anomaly detection:** unusual scan volume or repeated scope
  probing trips the kill switch.
- **Everything audited:** every scan, every finding, every refusal — with the
  ownership record and scope token referenced.
- **Dual-use knowledge:** the agent will explain defensive concepts and
  analyze the user's own artifacts, but declines to produce
  generally-applicable attack instructions, matching NELA's global safety
  posture.

## 8. Roadmap fit

- **NELA 1.0:** passive only — code/log/config audit and reports (T0/T1). No
  lab, no network. This is genuinely useful and fully safe.
- **NELA 2.0:** Isolated Cyber Lab for user-created practice targets; T3
  scanning of lab-only systems; educational CVE walkthroughs.
- **NELA 3.0:** richer lab (multi-host scenarios), continuous passive
  monitoring of the user's own systems with alerting — still no offensive
  capability, ever.
