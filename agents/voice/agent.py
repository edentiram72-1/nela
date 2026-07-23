"""Voice output Agent for NELA OS."""

from __future__ import annotations

from agents.base import AgentCommand, AgentResult, AgentState, BaseAgent
from core.events import EventBus, EventTypes
from voice.events import publish_voice_event
from voice.playback import PlaybackState
from voice.providers.base import SpeechProvider
from voice.providers.macos import MacOSSpeechProvider
from voice.queue import SpeechQueue, SpeechRequest
from voice.voice_profile import VoiceProfile


class VoiceAgent(BaseAgent):
    """Speaks final assistant responses through a replaceable provider."""

    name = "voice"
    capability = "voice"

    def __init__(
        self,
        events: EventBus | None = None,
        provider: SpeechProvider | None = None,
        enabled: bool = True,
        silent: bool = True,
        profile: VoiceProfile | None = None,
    ) -> None:
        super().__init__()
        self.events = events or EventBus()
        self.provider = provider or MacOSSpeechProvider()
        self.profile = profile or VoiceProfile()
        self.queue = SpeechQueue()
        self.playback = PlaybackState(enabled=enabled)
        self.silent = silent

    def initialize(self) -> AgentResult:
        self._state = AgentState.READY
        publish_voice_event(
            self.events,
            EventTypes.VOICE_STATUS_CHANGED,
            self._status_payload(),
        )
        return AgentResult(True, "voice initialized.", self._status_payload())

    def execute(self, command: AgentCommand) -> AgentResult:
        actions = {
            "speak": self._speak,
            "queue": self._queue_only,
            "queue_speech": self._queue_only,
            "flush_queue": self._flush_queue,
            "stop": self._stop_speech,
            "stop_speaking": self._stop_speech,
            "interrupt": self._interrupt,
            "pause": self._pause,
            "resume": self._resume,
            "set_enabled": self._set_enabled,
            "configure_profile": self._configure_profile,
            "status": self._status_result,
        }
        handler = actions.get(command.action)
        if handler is None:
            return AgentResult(
                False,
                f"Unsupported voice action: {command.action}",
                {"supported_actions": sorted(actions)},
            )
        try:
            return handler(command)
        except Exception as error:
            self._state = AgentState.ERROR
            publish_voice_event(
                self.events,
                EventTypes.SPEECH_FAILED,
                {"action": command.action, "error": str(error), "error_type": error.__class__.__name__},
            )
            return AgentResult(
                False,
                f"Voice action failed: {error}",
                {"action": command.action, "error": str(error), "error_type": error.__class__.__name__},
            )

    def stop(self) -> AgentResult:
        result = self._stop_speech(AgentCommand(action="stop"))
        self._state = AgentState.STOPPED
        return result

    def health_check(self) -> AgentResult:
        provider_health = self.provider.health_check()
        ok = bool(provider_health.get("available", True)) and self._state != AgentState.ERROR
        return AgentResult(
            ok,
            f"voice health is {'ok' if ok else 'not ok'}.",
            {
                **self._status_payload(),
                "provider_health": provider_health,
            },
        )

    def _speak(self, command: AgentCommand) -> AgentResult:
        request = self._request_from_command(command, interrupt=bool(command.payload.get("interrupt", False)))
        if request.interrupt:
            self.provider.stop()
            publish_voice_event(self.events, EventTypes.SPEECH_INTERRUPTED, {"reason": "interrupt"})
        self.queue.enqueue(request)
        publish_voice_event(self.events, EventTypes.SPEECH_QUEUED, self._request_payload(request))
        return self._process_next()

    def _queue_only(self, command: AgentCommand) -> AgentResult:
        request = self._request_from_command(command, interrupt=bool(command.payload.get("interrupt", False)))
        self.queue.enqueue(request)
        publish_voice_event(self.events, EventTypes.SPEECH_QUEUED, self._request_payload(request))
        return AgentResult(
            True,
            "Speech queued.",
            {**self._request_payload(request), "queue_size": len(self.queue)},
        )

    def _flush_queue(self, command: AgentCommand) -> AgentResult:
        results = []
        while len(self.queue):
            result = self._process_next()
            results.append(result.data)
            if not result.success:
                return result
        return AgentResult(True, "Speech queue flushed.", {"items": results, "queue_size": len(self.queue)})

    def _process_next(self) -> AgentResult:
        request = self.queue.next()
        if request is None:
            return AgentResult(True, "No speech queued.", {"queue_size": 0})

        silent = self.silent if request.silent is None else request.silent
        if not self.playback.enabled or silent:
            publish_voice_event(
                self.events,
                EventTypes.SPEECH_COMPLETED,
                {**self._request_payload(request), "spoken": False, "silent": silent},
            )
            return AgentResult(
                True,
                "Speech skipped because voice output is disabled or silent.",
                {**self._request_payload(request), "spoken": False, "silent": silent, "queue_size": len(self.queue)},
            )

        try:
            self._state = AgentState.RUNNING
            publish_voice_event(self.events, EventTypes.SPEECH_STARTED, self._request_payload(request))
            utterance_id = self.provider.speak(request.text, request.profile)
            self.playback.current_utterance_id = utterance_id
            self._state = AgentState.READY
            publish_voice_event(
                self.events,
                EventTypes.SPEECH_COMPLETED,
                {**self._request_payload(request), "utterance_id": utterance_id, "spoken": True},
            )
            return AgentResult(
                True,
                "Speech submitted to provider.",
                {
                    **self._request_payload(request),
                    "utterance_id": utterance_id,
                    "spoken": True,
                    "queue_size": len(self.queue),
                },
            )
        except Exception as error:
            self._state = AgentState.ERROR
            publish_voice_event(
                self.events,
                EventTypes.SPEECH_FAILED,
                {**self._request_payload(request), "error": str(error), "error_type": error.__class__.__name__},
            )
            return AgentResult(
                False,
                f"Speech failed: {error}",
                {
                    **self._request_payload(request),
                    "error": str(error),
                    "error_type": error.__class__.__name__,
                    "queue_size": len(self.queue),
                },
            )

    def _stop_speech(self, command: AgentCommand) -> AgentResult:
        self.provider.stop()
        self.queue.clear()
        self.playback.current_utterance_id = None
        self.playback.paused = False
        publish_voice_event(self.events, EventTypes.SPEECH_INTERRUPTED, {"reason": "stop"})
        return AgentResult(True, "Speech stopped.", self._status_payload())

    def _interrupt(self, command: AgentCommand) -> AgentResult:
        self.provider.stop()
        self.queue.clear()
        publish_voice_event(self.events, EventTypes.SPEECH_INTERRUPTED, {"reason": "interrupt"})
        text = str(command.payload.get("text", "")).strip()
        if text:
            return self._speak(AgentCommand(action="speak", payload={**command.payload, "interrupt": True}))
        return AgentResult(True, "Speech interrupted.", self._status_payload())

    def _pause(self, command: AgentCommand) -> AgentResult:
        try:
            self.provider.pause()
        except NotImplementedError as error:
            return AgentResult(False, str(error), self._status_payload())
        self.playback.paused = True
        publish_voice_event(self.events, EventTypes.SPEECH_PAUSED, self._status_payload())
        return AgentResult(True, "Speech paused.", self._status_payload())

    def _resume(self, command: AgentCommand) -> AgentResult:
        try:
            self.provider.resume()
        except NotImplementedError as error:
            return AgentResult(False, str(error), self._status_payload())
        self.playback.paused = False
        publish_voice_event(self.events, EventTypes.SPEECH_RESUMED, self._status_payload())
        return AgentResult(True, "Speech resumed.", self._status_payload())

    def _set_enabled(self, command: AgentCommand) -> AgentResult:
        enabled = bool(command.payload.get("enabled", True))
        self.playback.enabled = enabled
        if "silent" in command.payload:
            self.silent = bool(command.payload["silent"])
        publish_voice_event(self.events, EventTypes.VOICE_STATUS_CHANGED, self._status_payload())
        return AgentResult(True, "Voice status updated.", self._status_payload())

    def _configure_profile(self, command: AgentCommand) -> AgentResult:
        self.profile = VoiceProfile.from_dict({**self.profile.__dict__, **command.payload})
        publish_voice_event(self.events, EventTypes.VOICE_STATUS_CHANGED, self._status_payload())
        return AgentResult(True, "Voice profile updated.", self._status_payload())

    def _status_result(self, command: AgentCommand) -> AgentResult:
        return AgentResult(True, "Voice status.", self._status_payload())

    def _request_from_command(self, command: AgentCommand, interrupt: bool) -> SpeechRequest:
        text = str(command.payload.get("text", "")).strip()
        if not text:
            raise ValueError("Voice speech requires non-empty text.")
        profile = self.profile
        if isinstance(command.payload.get("profile"), dict):
            profile = VoiceProfile.from_dict({**profile.__dict__, **command.payload["profile"]})
        silent = command.payload.get("silent")
        return SpeechRequest(
            text=text,
            profile=profile,
            interrupt=interrupt,
            silent=bool(silent) if silent is not None else None,
        )

    def _request_payload(self, request: SpeechRequest) -> dict[str, object]:
        return {
            "request_id": request.id,
            "text": request.text,
            "profile": request.profile.name,
            "language": request.profile.language,
            "provider": self.provider.name,
        }

    def _status_payload(self) -> dict[str, object]:
        return {
            "enabled": self.playback.enabled,
            "silent": self.silent,
            "paused": self.playback.paused,
            "queue_size": len(self.queue),
            "current_utterance_id": self.playback.current_utterance_id,
            "profile": self.profile.name,
            "provider": self.provider.name,
            "state": self._state.value,
        }
