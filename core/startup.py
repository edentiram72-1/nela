"""Runtime bootstrap for NELA OS."""

from __future__ import annotations

from dataclasses import dataclass

from agents.automation.agent import AutomationAgent
from agents.browser.agent import BrowserAgent
from agents.calendar.agent import CalendarAgent
from agents.claude.agent import ClaudeAgent
from agents.codex.agent import CodexAgent
from agents.desktop.agent import DesktopAgent
from agents.files.agent import FilesAgent
from agents.github.agent import GitHubAgent
from agents.gmail.agent import GmailAgent
from agents.spotify.agent import SpotifyAgent
from agents.terminal.agent import TerminalAgent
from agents.vision.agent import VisionAgent
from brain.context import ContextEngine
from brain.conversation import ConversationEngine
from brain.decision import DecisionEngine
from brain.dispatcher import AgentDispatcher
from brain.intent_router import IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Planner
from core.config import AppConfig
from core.events import EventBus
from core.logger import configure_logging
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory


@dataclass
class NelaRuntime:
    config: AppConfig
    events: EventBus
    conversation: ConversationEngine
    dispatcher: AgentDispatcher
    context: ContextEngine
    memory: MemoryManager


def bootstrap(config: AppConfig | None = None) -> NelaRuntime:
    runtime_config = config or AppConfig.from_env()
    configure_logging(level=runtime_config.log_level)

    events = EventBus()
    dispatcher = AgentDispatcher(events=events)
    _register_builtin_agents(dispatcher)
    context = ContextEngine()
    memory = MemoryManager(
        short_term=ShortTermMemory(),
        long_term=LongTermMemory(),
        events=events,
    )
    conversation = ConversationEngine(
        intent_router=IntentRouter(),
        decision_engine=DecisionEngine(),
        planner=Planner(),
        memory=memory,
        context=context,
        dispatcher=dispatcher,
        events=events,
    )

    return NelaRuntime(
        config=runtime_config,
        events=events,
        conversation=conversation,
        dispatcher=dispatcher,
        context=context,
        memory=memory,
    )


def _register_builtin_agents(dispatcher: AgentDispatcher) -> None:
    for agent in (
        TerminalAgent(),
        BrowserAgent(),
        SpotifyAgent(),
        FilesAgent(),
        CalendarAgent(),
        GmailAgent(),
        GitHubAgent(),
        ClaudeAgent(),
        CodexAgent(),
        AutomationAgent(),
        VisionAgent(),
        DesktopAgent(),
    ):
        dispatcher.register_agent(agent)
