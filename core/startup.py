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
from agents.memory.agent import MemoryAgent
from agents.spotify.agent import SpotifyAgent
from agents.terminal.agent import TerminalAgent
from agents.voice.agent import VoiceAgent
from agents.vision.agent import VisionAgent
from brain.context import ContextEngine
from brain.conversation import ConversationEngine
from brain.decision import DecisionEngine
from brain.dispatcher import AgentDispatcher
from brain.intent_router import IntentRouter
from brain.memory_manager import MemoryManager
from brain.planner import Planner
from brain.qa import KnowledgeEngine
from core.config import AppConfig
from core.events import EventBus
from core.logger import configure_logging
from core.response import NelaResponseAdapter
from language.engine import HebrewLanguageEngine, LanguageEngine
from language.learning_store import LearnedResponseStore
from memory.long_term import LongTermMemory
from memory.short_term import ShortTermMemory
from voice.providers.factory import create_speech_provider
from agents.factory import build_default_agents


@dataclass
class NelaRuntime:
    config: AppConfig
    events: EventBus
    conversation: ConversationEngine
    dispatcher: AgentDispatcher
    context: ContextEngine
    memory: MemoryManager
    language: LanguageEngine
    response_adapter: NelaResponseAdapter


def bootstrap(config: AppConfig | None = None) -> NelaRuntime:
    runtime_config = config or AppConfig.from_env()
    configure_logging(level=runtime_config.log_level)

    events = EventBus()
    dispatcher = AgentDispatcher(events=events)
    learned_responses = LearnedResponseStore(runtime_config.data_dir / "language" / "learned_responses.json")
    _register_builtin_agents(dispatcher, events, runtime_config, learned_responses)
    language = HebrewLanguageEngine(personality_name=runtime_config.language_personality)
    response_adapter = NelaResponseAdapter(language=language, dispatcher=dispatcher, config=runtime_config)
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
        knowledge=KnowledgeEngine(learned_responses=learned_responses),
    )

    return NelaRuntime(
        config=runtime_config,
        events=events,
        conversation=conversation,
        dispatcher=dispatcher,
        context=context,
        memory=memory,
        language=language,
        response_adapter=response_adapter,
    )


def _register_builtin_agents(
    dispatcher: AgentDispatcher,
    events: EventBus,
    config: AppConfig,
    learned_responses: LearnedResponseStore,
) -> None:
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
        VoiceAgent(
            events=events,
            provider=create_speech_provider(config.voice_provider),
            enabled=config.enable_voice,
            silent=config.voice_silent_mode,
        ),
        VisionAgent(),
        MemoryAgent(),
        DesktopAgent(),
    ):
        dispatcher.register_agent(agent)

    _register_specialist_agents(dispatcher, config, learned_responses)


def _register_specialist_agents(
    dispatcher: AgentDispatcher,
    config: AppConfig,
    learned_responses: LearnedResponseStore,
) -> None:
    """Register first-wave specialist Agents without replacing live runtime Agents."""

    registered = set(dispatcher.discover_agents())
    learning_store_path = config.data_dir / "language" / "learned_responses.json"
    for agent in build_default_agents(learning_store_path=learning_store_path, learning_store=learned_responses):
        if agent.name in registered:
            continue
        dispatcher.register_agent(agent)
        registered.add(agent.name)
