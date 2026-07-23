import unittest

from core.events import Event, EventBus, EventTypes


class EventBusTests(unittest.TestCase):
    def test_event_bus_publishes_to_named_subscribers(self) -> None:
        bus = EventBus()
        received = []

        bus.subscribe(EventTypes.TASK_CREATED, received.append)
        event = Event(type=EventTypes.TASK_CREATED, source="test")

        bus.publish(event)

        self.assertEqual(received, [event])
        self.assertEqual(bus.history(), (event,))

    def test_event_bus_publishes_to_wildcard_subscribers(self) -> None:
        bus = EventBus()
        received = []

        bus.subscribe("*", received.append)
        event = Event(type=EventTypes.INTENT_RECOGNIZED, source="test")

        bus.publish(event)

        self.assertEqual(received, [event])


if __name__ == "__main__":
    unittest.main()
