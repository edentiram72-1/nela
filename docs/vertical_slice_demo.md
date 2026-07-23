# NELA Vertical Slice Demo

## Purpose

This document describes the first visible end-to-end NELA desktop demo.

The demo is integration-only. It does not redesign the Brain, add new Agents, or introduce Browser, Vision, Cyber, or advanced Coding features.

## Launch Command

```bash
python3 -m nela_runtime
```

The command starts a local server on `127.0.0.1`, opens the default browser, and serves the NELA demo UI.

Useful options:

```bash
python3 -m nela_runtime --no-open
python3 -m nela_runtime --port 8765
python3 -m nela_runtime --headless-smoke
```

Voice output is controlled by the existing environment settings:

```bash
NELA_VOICE_SILENT_MODE=false python3 -m nela_runtime
```

## UI Host Decision

The vertical slice uses a local browser-hosted UI as the smallest safe WebView-capable host.

Reason:

- It renders `design/nela_living_eye.html` with the real browser engine.
- It preserves Claude's animated HTML/SVG/CSS Living Eye instead of rewriting it as a static image.
- It requires no new heavy desktop runtime dependency.
- It keeps the current Brain, Language Engine, Voice Agent, Desktop Agent, and UI Event Bridge intact.

This is a demo host, not the final production shell. A future production app can replace it with Tauri, Electron, Python WebView, or another native WebView wrapper while keeping the same state bridge.

## Flow

```text
User Hebrew text
  -> Local browser UI
  -> NelaDemoController
  -> UIRouter
  -> ConversationEngine
  -> IntentRouter
  -> DecisionEngine
  -> Planner
  -> AgentDispatcher
  -> DesktopAgent / VoiceAgent
  -> LanguageEngine response
  -> UI chat
  -> Living Eye state updates
  -> IDLE
```

## Supported Demo Command

```text
נלה, תפתחי את Spotify
```

Expected behavior:

- Intent: `OpenApplication`
- Application: `Spotify`
- Planned task: `desktop.launch_application`
- Desktop execution: safe allowlisted `Spotify` lifecycle command
- Response: Hebrew response from the existing Language Engine and Claude language pack
- Voice: same response is sent to `VoiceAgent`; it speaks only when voice is enabled and silent mode is disabled
- Final Eye state: `idle`

## Event-To-Eye Mapping

The demo uses the existing `UIEventBridge` mapping:

| Event | Eye state |
|---|---|
| `InputReceived` | `listening` |
| `IntentRecognized` | `thinking` |
| `DecisionMade` | `thinking` |
| `TaskDispatched` | `executing` |
| `TaskStarted` | `executing` |
| `ConfirmationRequested` | `waiting` |
| `TaskCompleted` | `success` |
| `TaskFailed` | `error` |
| `AgentUnavailable` | `error` |
| `SpeechStarted` | `speaking` |
| `SpeechCompleted` | `idle` |
| `SpeechFailed` | `error` |
| `ConversationEnded` | `idle` |

The Voice Agent's generic `TaskCompleted` event does not override `SpeechCompleted -> idle`.

## Safety Boundaries

- Desktop actions remain limited to the current `DesktopAgent` allowlist.
- The demo does not execute arbitrary shell commands.
- The demo does not add Browser, Vision, Cyber, or advanced Coding features.
- Confirmation behavior remains owned by the current Brain and Decision Engine.
- Memory subsystem integration remains blocked until the missing ZIP is provided.
- The 94 untracked duplicate files remain untouched.

## Tests

Primary validation:

```bash
python3 -m scripts.validate_language_packs
python3 -m unittest discover -s tests
python3 -m ui.app --headless-smoke
python3 -m nela_runtime --headless-smoke
```

Latest result on `feature/NELA-vertical-slice-demo`: 68 tests passed, language validation passed, UI headless smoke passed, vertical-slice runtime headless smoke passed, and the Hebrew Spotify CLI smoke succeeded.

End-to-end integration test:

```bash
python3 -m unittest tests.test_vertical_slice_demo
```

The integration test uses mock Desktop and Voice providers so it does not launch real applications or play audio.
