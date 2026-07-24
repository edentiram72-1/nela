# Capability Routing

Status: implemented foundation on `feature/NELA-safety-spine-routing`.

## Purpose

Capability routing prevents user text from directly choosing privileged Agents.
The user asks for an outcome; NELA converts that into structured intent, then
semantic capabilities, then authorized Agent candidates.

## Required Order

```text
Intent
-> candidate capability set
-> policy eligibility
-> authorized candidate set
-> Agent selection
-> final scope validation
-> execution
```

## Current Flow

1. `brain.intent_router.IntentRouter` extracts structured intent fields.
2. `brain.planner.Planner` creates Tasks with semantic `capability` IDs.
3. `brain.dispatcher.AgentDispatcher` asks the Capability Registry for candidate
   Agents.
4. The Permission Engine authorizes each candidate before final selection.
5. The selected Agent receives the command only after authorization succeeds.

## Example

Hebrew input:

```text
נלה, תפתחי את ספוטיפיי
```

Planning result:

```text
Intent: OpenApplication
Application: Spotify
Task capability: desktop.application.launch
Agent selected after authorization: desktop
Tier: T1
```

The user does not need to know the internal Agent name.

## Prompt Injection Boundary

Untrusted text must never become authority. Current mitigations:

- Agent selection is based on structured fields and manifest capabilities.
- Application aliases are resolved from an allowlist.
- Unknown capabilities and unknown actions deny by default.
- Terminal and Coding side-effecting capabilities are present only as disabled
  declarations.

Future Browser, Research, Coding, and Cyber Agents must keep webpage or document
content out of Agent selection authority.
