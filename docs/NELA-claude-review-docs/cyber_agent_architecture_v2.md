# Defensive Cyber Agent — Architecture v2

Deepens `cyber_agent_spec.md` with the architecture, isolation mechanics, and
ownership verification needed before any T3 capability is built.

**The boundaries from v1 are unchanged and non-negotiable:** defensive,
educational, authorized-only, isolated-lab-only. This document adds *how the
isolation is enforced*, not what is permitted.

---

## 1. Component architecture

The agent is deliberately split so that the component holding lab network
access is small, isolated, and incapable of reaching anything else.

```text
┌──────────────────────────────────────────────┐
│ HOST SIDE                                     │
│                                               │
│  Cyber Analyst (T0/T1)                        │
│   · code / config / log analysis, offline     │
│   · CVE knowledge, remediation authoring      │
│   · report generation                         │
│   · NO network, NO lab access                 │
│                                               │
│  Lab Controller (T3, gated)                   │
│   · creates/destroys lab environments         │
│   · holds ownership records + scope tokens    │
│   · one-way audited channel in/out            │
└───────────────────┬──────────────────────────┘
                    │ audited one-way report channel
┌───────────────────▼──────────────────────────┐
│ LAB SIDE (isolated)                           │
│  Lab Runner                                   │
│   · executes scans inside the closed subnet   │
│   · no host mount, no internet route          │
│   · ephemeral, destroyed with the session     │
│  Lab Targets (user-created practice systems)  │
└──────────────────────────────────────────────┘
```

**The Analyst never touches the network. The Runner never touches the host.**
Neither component alone can both reach a target and reach the user's real
environment — that separation is the core safety property.

## 2. Ownership verification

No T3 action proceeds without an ownership record. Ownership is not established
by the user *claiming* it — claims are not verifiable and a design that accepts
them is a design that scans third parties on request.

**Ownership is structural:** a valid target is one that exists *inside the NELA
lab*, because the user created or imported it there. The lab subnet has no
route outward (§3), so there is no code path that reaches an external address.
Externally-supplied IPs, hostnames, and URLs are rejected at scope validation
as out-of-scope — this is a T4 refusal, not a permission prompt.

Record contents:

```yaml
lab_target:
  id: <lab-internal id>
  created_by: user | import
  created_at: <iso>
  lab_session: <session id>
  subnet: <lab-internal CIDR>
  expires_with_session: true
```

There is deliberately **no field for an external target**, no
"authorization letter" upload, and no override flag. Adding one would make the
whole design negotiable, which is exactly what must not happen.

## 3. Lab isolation mechanics

All five properties are required; the lab does not start if any is unverified:

1. **Network:** closed virtual subnet. No default route, no NAT, no DNS to the
   outside. Verified at lab boot by an egress test that *must fail*.
2. **Filesystem:** the Runner has no bind mount, no shared volume, no host
   path. Results leave only as structured text through the report channel.
3. **Report channel:** one-way, audited, size-bounded, content-typed
   (findings only — never binaries, never archives, never executables).
4. **Ephemerality:** environments are created per session and destroyed after.
   Snapshots exist only for rollback within the session.
5. **Coupled teardown:** losing the audit channel, tripping the kill switch, or
   ending the session tears the lab down automatically.

**Egress test as a gate:** before any scan is permitted, the Runner attempts to
reach a known external host and to reach the host machine. Both must fail. If
either succeeds, the lab is destroyed and the capability is disabled until an
operator investigates. Isolation is verified, not assumed.

## 4. Permission integration

| Action | Tier | Gate |
| --- | --- | --- |
| Analyze provided code/logs/configs | T0 | none |
| Explain a vulnerability class or CVE | T0 | none |
| Write a security report | T1 | scope: report dir |
| Create/destroy a lab environment | T3 | elevation + confirm |
| Inventory lab targets | T3 | lab session + scope token |
| Scan a lab target for known vulns | T3 | lab session + scope token + confirm |
| Non-destructive validation of a finding | T3 | as above, per-finding confirm |
| Anything against a non-lab target | **T4** | refused, audited as an anomaly |
| Destructive payloads, exploit development, persistence | **T4** | refused |

T3 requires *fresh* elevation (`auth_session_lock_model.md` §2): lab
authorization does not survive lock, session expiry, or restart.

## 5. Audit specifics

Beyond the standard record, every T3 action logs: the lab session id, the
ownership record id, the scope token, the target's lab-internal identifier, the
scan type, and the egress-test result that authorized the session.

**Refusals are logged as loudly as actions.** A T4 refusal against a
non-lab target is an anomaly signal — a repeated pattern trips the kill switch
and surfaces to the user. This matters more here than anywhere else in NELA: a
system being probed for offensive use should make that visible.

## 6. Reporting and remediation

- Findings are prioritized (severity × exploitability × asset value) with
  CVE/CWE references and **minimal, concrete** remediations.
- The agent recommends; it never applies a fix to the audited system. Applying
  is a separate Coding-Agent task with its own plan, review, and confirmation.
- Educational output explains the mechanism of a vulnerability class without
  supplying working attack tooling — understanding, not weaponry.
- Reports contain no exploit code. A finding is described by its signature and
  effect, not by a runnable proof.

## 7. Failure modes

| Failure | Behaviour |
| --- | --- |
| Egress test passes (isolation broken) | destroy lab, disable T3, alarm |
| Report channel unavailable | tear down lab; no findings escape unaudited |
| Lab session expires mid-scan | scan abandoned, outcome `unknown`, lab destroyed |
| Ownership record missing/expired | T3 denied |
| Non-lab target requested | T4 refusal + anomaly signal |
| Kill switch during a scan | lab destroyed, tokens revoked, outcome `unknown` |

## 8. Tests required

1. Lab egress to the internet fails; lab egress to the host fails.
2. External IP/hostname/URL as a target ⇒ refused at scope validation (T4).
3. No override, flag, or config makes an external target acceptable.
4. Report channel rejects non-text content and oversized payloads.
5. Kill switch mid-scan destroys the lab and records `unknown`.
6. Expired elevation ⇒ T3 denied even inside a live lab session.
7. Repeated T4 refusals trip anomaly detection.
8. Findings contain no executable content (asserted on report output).

## 9. Roadmap position

- **1.0:** Analyst only — passive audits and reports, no network, no lab. Fully
  useful and structurally incapable of misuse.
- **2.0:** Lab Controller + Runner for user-created practice targets; T3
  scanning with per-session elevation.
- **3.0:** richer multi-host lab scenarios; continuous *passive* monitoring of
  the user's own systems with alerting. Offensive capability remains out of
  scope permanently — it is not a roadmap item deferred, it is excluded.
