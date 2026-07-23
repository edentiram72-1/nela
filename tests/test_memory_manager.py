import unittest

from brain.intent_router import IntentRouter
from brain.memory_manager import MemoryManager
from core.events import EventBus, EventTypes
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory


class MemoryManagerTests(unittest.TestCase):
    def test_records_short_and_long_term_memory_events(self) -> None:
        events = EventBus()
        memory = MemoryManager(ShortTermMemory(), LongTermMemory(), events)
        intent = IntentRouter().classify("Remember that I prefer quiet music")

        memory.record_turn("Remember that I prefer quiet music", intent)
        item = memory.remember("I prefer quiet music", tags=("preference",))

        self.assertEqual(memory.short_term.recent()[0].intent, "Remember")
        self.assertEqual(memory.long_term.all(), (item,))
        self.assertEqual(
            [event.type for event in events.history()],
            [EventTypes.MEMORY_UPDATED, EventTypes.MEMORY_UPDATED],
        )


if __name__ == "__main__":
    unittest.main()

