import unittest

from agents.base import AgentCommand
from agents.voice.agent import VoiceAgent
from core.events import EventBus, EventTypes
from voice.providers.mock import MockSpeechProvider
from voice.voice_profile import VoiceProfile


class VoiceAgentTests(unittest.TestCase):
    def test_voice_profile_from_dict(self) -> None:
        profile = VoiceProfile.from_dict({"name": "soft", "rate": 0.8, "volume": 0.7})

        self.assertEqual(profile.name, "soft")
        self.assertEqual(profile.language, "he-IL")
        self.assertEqual(profile.rate, 0.8)
        self.assertEqual(profile.volume, 0.7)

    def test_speak_uses_provider_and_events(self) -> None:
        events = EventBus()
        provider = MockSpeechProvider()
        agent = VoiceAgent(events=events, provider=provider, enabled=True, silent=False)

        result = agent.execute(AgentCommand(action="speak", payload={"text": "שלום"}))

        self.assertTrue(result.success)
        self.assertEqual(provider.spoken[0][0], "שלום")
        event_types = [event.type for event in events.history()]
        self.assertIn(EventTypes.SPEECH_QUEUED, event_types)
        self.assertIn(EventTypes.SPEECH_STARTED, event_types)
        self.assertIn(EventTypes.SPEECH_COMPLETED, event_types)

    def test_queue_behavior(self) -> None:
        provider = MockSpeechProvider()
        agent = VoiceAgent(provider=provider, enabled=True, silent=False)

        queued = agent.execute(AgentCommand(action="queue_speech", payload={"text": "אחד"}))
        flushed = agent.execute(AgentCommand(action="flush_queue"))

        self.assertTrue(queued.success)
        self.assertTrue(flushed.success)
        self.assertEqual(provider.spoken[0][0], "אחד")

    def test_stop_interrupts_and_clears_queue(self) -> None:
        provider = MockSpeechProvider()
        agent = VoiceAgent(provider=provider, enabled=True, silent=False)
        agent.execute(AgentCommand(action="queue_speech", payload={"text": "אחד"}))

        result = agent.execute(AgentCommand(action="stop"))

        self.assertTrue(result.success)
        self.assertTrue(provider.stopped)
        self.assertEqual(result.data["queue_size"], 0)

    def test_provider_failure_returns_structured_error(self) -> None:
        agent = VoiceAgent(provider=MockSpeechProvider(fail=True), enabled=True, silent=False)

        result = agent.execute(AgentCommand(action="speak", payload={"text": "שלום"}))

        self.assertFalse(result.success)
        self.assertEqual(result.data["error_type"], "RuntimeError")

    def test_silent_mode_does_not_call_provider(self) -> None:
        provider = MockSpeechProvider()
        agent = VoiceAgent(provider=provider, enabled=True, silent=True)

        result = agent.execute(AgentCommand(action="speak", payload={"text": "שקט"}))

        self.assertTrue(result.success)
        self.assertFalse(result.data["spoken"])
        self.assertEqual(provider.spoken, [])


if __name__ == "__main__":
    unittest.main()
