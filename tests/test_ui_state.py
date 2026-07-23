import unittest

from core.events import Event, EventBus, EventTypes
from ui.events import UIEventBridge
from ui.state import EyeState, MessageRole, UIStateManager
from ui.theme import ThemeManager, ThemeName


class UIStateTests(unittest.TestCase):
    def test_state_manager_tracks_chat_and_streaming(self) -> None:
        state = UIStateManager()
        message = state.add_message(MessageRole.ASSISTANT, "", streaming=True)

        state.append_to_message(message.id, "hello", streaming=True)
        state.finish_streaming_message(message.id)

        self.assertEqual(state.state.messages[0].content, "hello")
        self.assertFalse(state.state.messages[0].streaming)

    def test_theme_manager_switches_theme(self) -> None:
        manager = ThemeManager()

        theme = manager.switch(ThemeName.LIGHT)

        self.assertEqual(theme.name, ThemeName.LIGHT)
        self.assertEqual(manager.active_name, ThemeName.LIGHT)

    def test_event_bridge_maps_brain_events_to_eye_states(self) -> None:
        bus = EventBus()
        state = UIStateManager()
        bridge = UIEventBridge(bus, state)

        bridge.start()
        bus.publish(Event(type=EventTypes.INTENT_RECOGNIZED, source="test"))
        self.assertEqual(state.state.eye_state, EyeState.THINKING)

        bus.publish(Event(type=EventTypes.DECISION_MADE, source="test"))
        self.assertEqual(state.state.eye_state, EyeState.THINKING)

        bus.publish(Event(type=EventTypes.CONFIRMATION_REQUESTED, source="test"))
        self.assertEqual(state.state.eye_state, EyeState.WAITING)

        bus.publish(Event(type=EventTypes.TASK_DISPATCHED, source="test", payload={"task_id": "task-1"}))
        self.assertEqual(state.state.eye_state, EyeState.EXECUTING)

        bus.publish(Event(type=EventTypes.TASK_STARTED, source="test", payload={"task_id": "task-1"}))
        self.assertEqual(state.state.eye_state, EyeState.EXECUTING)

        bus.publish(Event(type=EventTypes.TASK_COMPLETED, source="test", payload={"task_id": "task-1"}))
        self.assertEqual(state.state.eye_state, EyeState.SUCCESS)

        bus.publish(Event(type=EventTypes.TASK_FAILED, source="test", payload={"message": "failed"}))
        self.assertEqual(state.state.eye_state, EyeState.ERROR)
        self.assertEqual(state.state.notifications[-1].message, "failed")

    def test_event_bridge_schedules_moment_states_back_to_idle(self) -> None:
        scheduled: list[tuple[int, object]] = []
        bus = EventBus()
        state = UIStateManager()
        bridge = UIEventBridge(bus, state, schedule_idle=lambda delay, callback: scheduled.append((delay, callback)))

        bridge.start()
        bus.publish(Event(type=EventTypes.TASK_COMPLETED, source="test", payload={"task_id": "task-1"}))

        self.assertEqual(state.state.eye_state, EyeState.SUCCESS)
        self.assertEqual(scheduled[0][0], 3000)
        scheduled[0][1]()
        self.assertEqual(state.state.eye_state, EyeState.IDLE)


if __name__ == "__main__":
    unittest.main()
