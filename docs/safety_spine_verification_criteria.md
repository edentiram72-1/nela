# Safety Spine Verification Criteria

Status: active mechanical acceptance checklist for Sprint 2 safety-spine review.

This document turns Claude's Sprint 2 architecture findings into repository
acceptance criteria. A criterion marked `[CRIT]` means a single failure is a
FAIL for that finding. Documentation claims are not enough; every PASS must be
supported by code and tests.

## A1: WebView Bridge Authentication

PASS criteria:

1. `[CRIT]` The local UI bridge uses a restricted local transport, preferably a
   Unix domain socket.
2. `[CRIT]` Socket filesystem permissions are restricted to the launching user.
3. `[CRIT]` Each launch generates a fresh token using a cryptographic random
   source.
4. `[CRIT]` Token comparison uses constant-time comparison.
5. `[CRIT]` The expected UI origin is verified.
6. `[CRIT]` The bridge never binds to `0.0.0.0`.
7. `[CRIT]` The UI bridge is not treated as the authority for permissions.

Mechanical indicators:

```text
socket.AF_UNIX
chmod(0o600)
secrets.token_urlsafe
hmac.compare_digest
expected_origin
```

Required evidence:

- `ui/secure_bridge.py`
- `tests/test_secure_bridge.py`

## K1: Kill Switch Process Isolation

PASS criteria:

1. `[CRIT]` Blocking or high-risk work has a subprocess isolation foundation.
2. `[CRIT]` Timeout behavior terminates the child process.
3. `[CRIT]` A revocation hook can run before termination.
4. `[CRIT]` The code does not claim Python threads can forcibly interrupt a
   blocked Agent.
5. A third result state, `unknown`, exists for process outcomes that cannot be
   safely classified.

Mechanical indicators:

```text
multiprocessing.Process
terminate()
kill()
ProcessOutcome.UNKNOWN
```

Required evidence:

- `agents/process_isolation.py`
- `tests/test_process_isolation.py`

## P1: TOCTOU Protection

PASS criteria:

1. `[CRIT]` Filesystem targets are canonicalized immediately before execution.
2. `[CRIT]` Scope is revalidated in the Dispatcher immediately before Agent
   execution.
3. `[CRIT]` Protected credential/security paths are denied.
4. Symlink escapes from an approved root are rejected.
5. Existing filesystem targets record stable file identity when available.

Mechanical indicators:

```text
resolve(strict=True)
st_dev
st_ino
_validate_execution_scope
```

Required evidence:

- `permissions/scope.py`
- `brain/dispatcher.py`
- `tests/test_permission_engine.py`

## P2: Confirmation Binding

PASS criteria:

1. `[CRIT]` A confirmation is bound to the exact action tuple.
2. `[CRIT]` The tuple includes Agent, capability, action, target, parameters,
   session, and expiration.
3. `[CRIT]` The Permission Engine recomputes the hash before execution.
4. `[CRIT]` A mismatched or expired confirmation is denied.

Mechanical indicators:

```text
action_tuple_hash
confirmation_action_hash
CONFIRMATION_MISMATCH
confirmation_expires_at
```

Required evidence:

- `permissions/confirmation.py`
- `permissions/engine.py`
- `brain/conversation.py`
- `brain/planner.py`
- `tests/test_conversation_confirmations.py`
- `tests/test_permission_engine.py`

## R1: Agent Registry Overwrite

PASS criteria:

1. `[CRIT]` Agent registration is insert-only by default.
2. `[CRIT]` Duplicate Agent IDs are rejected.
3. `[CRIT]` Replacement exists only through an explicit replacement flow.
4. Manifest identity and version are validated.
5. Registration, duplicate rejection, and replacement attempts are auditable.

Mechanical fail indicators:

```text
_agents[.*] =
register_manifest(... replace=True ...) without identity validation
```

Required evidence:

- `agents/registry.py`
- `permissions/registry.py`
- `tests/test_permission_engine.py`

## L1: Tamper-Evident Audit Log

PASS criteria:

1. `[CRIT]` Audit entries include `previous_hash`.
2. `[CRIT]` Audit entries include `entry_hash`.
3. `[CRIT]` The log can detect modification, deletion, or reordering.
4. `[CRIT]` Required audit write failures fail closed for T2/T3 authorization.
5. Durable sinks are flushed and `fsync`ed.

Mechanical indicators:

```text
previous_hash
entry_hash
verify_chain
AuditWriteError
os.fsync
```

Required evidence:

- `permissions/audit.py`
- `permissions/engine.py`
- `tests/test_audit_log.py`
- `tests/test_permission_engine.py`

## T1: Authorization Before Final Routing

PASS criteria:

1. `[CRIT]` The Planner emits semantic capabilities rather than choosing a
   privileged Agent from free text.
2. `[CRIT]` The Dispatcher builds a candidate Agent set from the Capability
   Registry.
3. `[CRIT]` The Dispatcher authorizes candidates before selecting an Agent.
4. `[CRIT]` Scope is validated again immediately before execution.
5. Agent selection cannot broaden the authorized capability.

Required order:

```text
Intent
-> candidate capability set
-> policy eligibility
-> authorized candidate set
-> Agent selection
-> final scope validation
-> execution
```

Required evidence:

- `brain/planner.py`
- `brain/dispatcher.py`
- `permissions/registry.py`
- `tests/test_dispatcher.py`

## T2: Prompt Injection Into Routing

PASS criteria:

1. Routing must use structured trusted intent fields, not untrusted document
   text as authority.
2. Application routing is constrained through a local alias allowlist.
3. Future Research/Browser/Coding agents must not pass untrusted page, README,
   email, or repository content into Agent selection as authority.

Current status: partially mitigated. This remains a future review point before
new content-ingesting Agents receive side effects.

Required evidence:

- `brain/applications.py`
- `brain/intent_router.py`
- `docs/sprint2_claude_findings_status.md`

## Codex Self-Check

Run before handing the branch back for review:

```text
rg -n "_agents\\[.*\\]\\s*=" agents permissions
rg -n "threading\\.Thread" agents brain permissions ui
rg -n "fsync|previous_hash|entry_hash|verify_chain" permissions tests
rg -n "AF_UNIX|chmod\\(0o600\\)|token_urlsafe|compare_digest" ui tests
rg -n "action_tuple_hash|confirmation_action_hash|CONFIRMATION_MISMATCH" permissions brain tests
python3 -m unittest discover -s tests
python3 -m scripts.validate_language_packs
python3 -m ui.app --headless-smoke
```

Expected result: no registry overwrite matches, no thread-based isolation
matches, and all validation commands pass.
