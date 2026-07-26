# Authentication, Scoped Sessions & Lock Mode

Specification for three subsystems introduced in Sprint 2 that were **not**
part of the original Phase A spine. They govern *who* is talking to NELA and
*for how long* — the layer beneath the Permission Engine, which governs *what*
may be done.

Companion: `permission_model.md` (tiers), `sprint2_architecture_review.md`
(threat findings A1–A3).

---

## 1. Threat model — what is actually being defended

NELA is a desktop application holding T2 (real side effects) and T3 (lab)
capabilities. The realistic adversaries, in order of likelihood:

| # | Adversary | Capability | Primary defence |
| --- | --- | --- | --- |
| 1 | Another **local process** on the same machine (browser tab, unprivileged app, malicious dependency) | can connect to any local socket/port | bridge authentication (§2) |
| 2 | Someone with **physical access** to an unlocked machine | full UI access | Lock Mode (§4) |
| 3 | **Untrusted content** processed by NELA (repo text, web pages, file contents) | prompt injection | content never influences authorization or routing |
| 4 | A **buggy or compromised agent** | acts within its manifest | tiers, scopes, quarantine |

The user themselves is *not* an adversary. Authentication exists to prove that
input claiming to come from the user actually does — not to restrict the user.

## 2. Authentication — the UI bridge

**This is the highest-risk new surface in Sprint 2.**

The webview UI communicates with the Python runtime through a bridge. If that
bridge is an HTTP server on localhost with no authentication, every local
process can drive NELA. A page in the user's browser could issue commands to a
system that closes applications, commits code, and holds lab authorization.

### Requirements (all mandatory)

1. **Transport:** prefer a **Unix domain socket** with `0600` permissions owned
   by the user. Filesystem permissions become the authentication boundary.
2. **If TCP is unavoidable:** bind `127.0.0.1` only — never `0.0.0.0`, never a
   LAN interface. Binding to a non-loopback interface is a T4-class defect.
3. **Per-launch bearer token:** generated at startup with a CSPRNG, injected
   into the webview at creation (not via a file, not via argv where it is
   visible in `ps`), required on every request. Rotated per launch.
4. **Origin/host validation:** reject requests whose `Origin` is not the
   webview's own; reject `null` origins.
5. **No GET side effects; CSRF-safe verbs.** A bridge endpoint that mutates
   state on GET is reachable from a plain `<img>` tag.
6. **Fail closed:** a request missing or failing any check is refused, audited
   as `BridgeAuthFailure`, and repeated failures trip anomaly detection.

### Re-authentication for elevation

High-tier actions may require a fresh proof of user presence, time-boxed
("sudo mode"): T3 lab authorization and any action touching the permission
engine, audit log, or secrets. Elevation is:

- explicit (the user acts to grant it),
- time-boxed on a **monotonic** clock (§3),
- single-scope (elevation for lab work does not elevate git pushes),
- revoked by Lock Mode and by the kill switch,
- audited on grant, use, and expiry.

## 3. Scoped Sessions

A session binds *authenticated presence* to *a bounded set of grants*.

```yaml
session:
  id: uuid
  created_at_monotonic: <ns>       # enforcement clock
  created_at_wall: <iso>           # display/audit only
  expires_after: <duration>
  idle_timeout: <duration>
  grants:                          # scope tokens issued under this session
    - {agent, action, targets, tier, expiry}
  elevation: {active: bool, scope: <string>, expires_at_monotonic: <ns>}
  host_id: <string>                # forward-compat for 3.0 multi-host
```

Rules:

1. **Monotonic enforcement.** Expiry is evaluated against a monotonic clock so
   changing the system clock cannot extend a session (review finding A3).
   Wall-clock timestamps are recorded for humans only.
2. **Grants are session-bound.** A scope token cannot outlive its session, be
   used by a different agent, or be replayed after revocation.
3. **Idle timeout** independent of absolute expiry.
4. **Revocation is immediate and global** — kill switch, lock, logout, and
   anomaly detection all revoke. Revocation is checked at *use* time, not
   cached.
5. **No silent renewal.** Extending a session requires the same proof as
   creating one. Auto-renewal on activity is permitted only for T0/T1 scopes.
6. **Sessions are not identity.** They never carry relationship stage, trust
   level, or personality state — those affect tone only, never permission
   (`permission_model.md` §7).

### Session ↔ task interaction

- A task's authorization is bound to the session that spawned it. If the
  session dies mid-plan, remaining tasks are not dispatched.
- In-flight behaviour on expiry: T0 continues; T1+ pauses at the next task
  boundary; in-flight T2/T3 resolves per the kill-switch rules (complete, or
  abandoned and recorded `unknown`).

## 4. Lock Mode

Lock Mode suspends NELA while preserving state. It is **distinct from the kill
switch** and the two must not be conflated:

| | Lock Mode | Kill Switch |
| --- | --- | --- |
| Intent | "I'm stepping away" | "Stop, something is wrong" |
| In-flight tasks | pause at next boundary | cancel / abandon |
| Scope tokens | suspended | revoked |
| Queue | preserved | drained |
| Recovery | re-authenticate → resume | explicit, audited, no token restore |
| Eye | locked visual | locked-`offline` visual |

### Requirements

1. **Voice does not bypass the lock (review finding A2).** While locked, the
   voice pipeline may reach *only* the unlock flow. A wake word does not open a
   conversation; NELA does not answer "אני איתך" to a locked machine. All other
   intents receive a lock notice.
2. **The eye must make lock state unmistakable** — a dedicated visual, not a
   variant of sleeping, because sleeping implies "will wake on call" and locked
   means "will not".
3. **No authorization while locked.** `authorize()` denies everything except
   the unlock action. Denials are audited (a burst of them is a signal).
4. **Auto-lock** on idle timeout and on system lock/sleep, configurable.
5. **Unlock requires authentication**, and unlocking does **not** restore
   elevation — elevation must be re-granted explicitly.
6. **Notifications while locked** may show that something happened, never the
   content (no message text, no file names) — the lock screen is a hostile
   surface by assumption.

## 5. Failure modes

| Failure | Behaviour |
| --- | --- |
| Bridge token lost / mismatch | refuse, audit, require UI restart |
| Session store unreadable | fail closed — everything T0 until restored |
| Clock jumps backwards | monotonic enforcement unaffected; log the anomaly |
| Lock state file corrupted | assume **locked** (fail secure) |
| Elevation grant survives a crash | it must not — elevation is memory-only, never persisted |
| Bridge reachable without token | treat as a security incident: kill switch + audit alarm |

## 6. Tests required

1. Bridge request with no token / wrong token / wrong origin ⇒ refused.
2. Bridge bound to a non-loopback interface ⇒ startup fails (assert in test).
3. Token not present in `ps` output or on disk.
4. Clock manipulation does not extend a session or elevation.
5. Wake word while locked reaches only the unlock flow.
6. Scope token unusable after lock, after session expiry, and by a second agent.
7. Elevation does not survive lock, kill switch, or process restart.
8. Corrupted lock state ⇒ locked.
9. Burst of denied authorizations while locked ⇒ anomaly signal.
10. Session death mid-plan ⇒ remaining tasks not dispatched.

## 7. Open decisions for the user

1. **Unlock factor.** OS-level (Touch ID / keychain prompt) is strongest and
   avoids NELA storing any credential. Recommended. A NELA-managed passphrase
   means NELA holds a secret it must protect — avoid if possible.
2. **Auto-lock default.** Recommend on, tied to OS screen lock.
3. **Whether elevation is ever persisted across restarts.** Recommendation: no,
   never — the cost is one extra prompt.
