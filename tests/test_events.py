import unittest
import time

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

    def test_failing_subscriber_does_not_block_other_subscribers(self) -> None:
        bus = EventBus()
        received = []

        def broken(_event: Event) -> None:
            raise RuntimeError("boom")

        bus.subscribe(EventTypes.TASK_CREATED, broken)
        bus.subscribe(EventTypes.TASK_CREATED, received.append)
        event = Event(type=EventTypes.TASK_CREATED, source="test", correlation_id="corr-1")

        bus.publish(event)

        self.assertEqual(received, [event])
        internal_events = [item for item in bus.history() if item.type == EventTypes.EVENT_SUBSCRIBER_FAILED]
        self.assertEqual(len(internal_events), 1)
        self.assertEqual(internal_events[0].correlation_id, "corr-1")

    def test_history_is_bounded(self) -> None:
        bus = EventBus(max_history=2)

        first = Event(type=EventTypes.INPUT_RECEIVED, source="test", payload={"order": 1})
        second = Event(type=EventTypes.INPUT_RECEIVED, source="test", payload={"order": 2})
        third = Event(type=EventTypes.INPUT_RECEIVED, source="test", payload={"order": 3})
        for event in (first, second, third):
            bus.publish(event)

        self.assertEqual(bus.history(), (second, third))

    def test_recursive_publish_is_detected(self) -> None:
        bus = EventBus(max_publish_depth=2)

        def recursive(event: Event) -> None:
            bus.publish(Event(type=event.type, source="recursive", correlation_id=event.correlation_id))

        bus.subscribe(EventTypes.INPUT_RECEIVED, recursive)
        bus.publish(Event(type=EventTypes.INPUT_RECEIVED, source="test", correlation_id="corr-loop"))

        loop_events = [event for event in bus.history() if event.type == EventTypes.EVENT_LOOP_DETECTED]
        self.assertEqual(len(loop_events), 1)
        self.assertEqual(loop_events[0].correlation_id, "corr-loop")

    def test_slow_subscriber_is_reported(self) -> None:
        bus = EventBus(slow_handler_seconds=0.001)

        def slow(_event: Event) -> None:
            time.sleep(0.002)

        bus.subscribe(EventTypes.TASK_STARTED, slow)
        bus.publish(Event(type=EventTypes.TASK_STARTED, source="test"))

        self.assertIn(EventTypes.EVENT_SUBSCRIBER_SLOW, [event.type for event in bus.history()])

    def test_event_order_is_preserved_for_normal_events(self) -> None:
        bus = EventBus()
        ordered = []

        bus.subscribe("*", lambda event: ordered.append(event.payload.get("order")))
        for order in range(3):
            bus.publish(Event(type=EventTypes.CONTEXT_UPDATED, source="test", payload={"order": order}))

        self.assertEqual(ordered, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
