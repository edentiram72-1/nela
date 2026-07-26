"""Application configuration for NELA OS."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Environment-neutral runtime configuration."""

    environment: str = "development"
    log_level: str = "INFO"
    data_dir: Path = Path("./data")
    plugin_dir: Path = Path("./plugins")
    enable_voice: bool = False
    enable_vision: bool = False
    language_personality: str = "default"
    voice_auto_speak_responses: bool = True
    voice_silent_mode: bool = True
    voice_provider: str = "macos_say"
    voice_profile: str = "nela_default"
    llm_enabled: bool = False
    llm_provider: str = "openai"
    llm_model: str = "gpt-5-mini"
    llm_timeout_seconds: float = 20.0

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            environment=os.getenv("NELA_ENV", "development"),
            log_level=os.getenv("NELA_LOG_LEVEL", "INFO"),
            data_dir=Path(os.getenv("NELA_DATA_DIR", "./data")),
            plugin_dir=Path(os.getenv("NELA_PLUGIN_DIR", "./plugins")),
            enable_voice=_env_bool("NELA_ENABLE_VOICE", default=False),
            enable_vision=_env_bool("NELA_ENABLE_VISION", default=False),
            language_personality=os.getenv("NELA_LANGUAGE_PERSONALITY", "default"),
            voice_auto_speak_responses=_env_bool("NELA_VOICE_AUTO_SPEAK_RESPONSES", default=True),
            voice_silent_mode=_env_bool("NELA_VOICE_SILENT_MODE", default=True),
            voice_provider=os.getenv("NELA_VOICE_PROVIDER", "macos_say"),
            voice_profile=os.getenv("NELA_VOICE_PROFILE", "nela_default"),
            llm_enabled=_env_bool("NELA_LLM_ENABLED", default=False),
            llm_provider=os.getenv("NELA_LLM_PROVIDER", "openai"),
            llm_model=os.getenv("NELA_LLM_MODEL", "gpt-5-mini"),
            llm_timeout_seconds=float(os.getenv("NELA_LLM_TIMEOUT_SECONDS", "20")),
        )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}
