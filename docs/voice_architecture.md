# NELA Voice Architecture

## Purpose

The Voice Agent speaks the final response that the Language System already rendered.

The Voice Agent does not select wording and does not contain personality rules. It receives text, queues it, sends it to a replaceable speech provider, reports status through events, and returns structured results.

## Flow

```text
Brain
  |
  v
NelaResponseAdapter
  |
  v
LanguageEngine renders Hebrew text
  |
  +--> UI message
  |
  v
AgentDispatcher
  |
  v
VoiceAgent
  |
  v
SpeechProvider
```

## Agent Contract

Module: `agents/voice/agent.py`

The Voice Agent implements the standard Agent contract:

```python
initialize()
execute(command)
stop()
status()
health_check()
```

Supported actions:

- `speak`
- `queue`
- `queue_speech`
- `flush_queue`
- `stop`
- `stop_speaking`
- `interrupt`
- `pause`
- `resume`
- `set_enabled`
- `configure_profile`
- `status`

## Provider Architecture

Providers implement `voice/providers/base.py`.

Current providers:

- `MacOSSpeechProvider`: local MVP provider using the built-in macOS `say` command. No API key is required.
- `MockSpeechProvider`: deterministic test provider that records text without producing audio.

Provider-specific code stays inside `voice/providers/`. The Language System never imports providers.

## Switching Providers

Provider selection is configured with:

```text
NELA_VOICE_PROVIDER=macos_say
```

The current provider factory supports:

- `macos_say`
- `mock`

Future providers can be added by implementing `SpeechProvider` and registering the name in `voice/providers/factory.py`.

Do not commit API keys. Future providers that require credentials must read them from environment variables or an external secret store.

## Voice Profile

Module: `voice/voice_profile.py`

`VoiceProfile` stores:

- `name`
- `language`
- `gender`
- `rate`
- `pitch`
- `volume`
- `style`
- `provider_voice`

The first profile is infrastructure only. Claude can later define production voice profiles and emotional rules.

## Events

Voice lifecycle events are defined in `core/events.py`:

- `SpeechQueued`
- `SpeechStarted`
- `SpeechPaused`
- `SpeechResumed`
- `SpeechCompleted`
- `SpeechInterrupted`
- `SpeechFailed`
- `VoiceStatusChanged`

## Configuration

Environment variables:

```text
NELA_ENABLE_VOICE=false
NELA_VOICE_AUTO_SPEAK_RESPONSES=true
NELA_VOICE_SILENT_MODE=true
NELA_VOICE_PROVIDER=macos_say
NELA_VOICE_PROFILE=nela_default
```

`NELA_VOICE_SILENT_MODE=true` keeps the full response pipeline active without audio output. This is the safe default for tests and early development.

## Privacy

The MVP macOS provider sends text only to the local `say` command. The test provider records text in memory only during the process.

Future cloud TTS providers may transmit response text outside the machine. Any such provider must be opt-in, documented, and covered by configuration and permission policy before it is enabled.

## Future Custom Voice Support

The current system does not clone, synthesize, or claim a custom NELA voice. It only stores profile metadata and speaks through the selected provider. A custom NELA voice can be added later behind the same `SpeechProvider` contract if a real provider supports it.

## Known Limitations

- The macOS `say` provider submits speech asynchronously and treats provider submission as completion.
- The macOS `say` provider does not support portable pause/resume.
- No remote TTS provider is configured.
- No wake-word or speech-to-text integration has been connected to the response path yet.
- Voice profile persistence is not implemented yet.

## Future Extensions

- Add provider registry and provider selection from config.
- Add high-quality Hebrew TTS providers behind the same contract.
- Add streaming speech events.
- Add synchronized subtitles and UI mouth/eye animation events.
- Add voice-profile language packs authored and reviewed by Claude.
