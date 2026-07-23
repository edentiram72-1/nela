"""Application configuration for NELA OS."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Environment-neutral runtime configuration."""

    environment: str
    log_level: str
    data_dir: Path
    plugin_dir: Path
    enable_voice: bool
    enable_vision: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        return cls(
            environment=os.getenv("NELA_ENV", "development"),
            log_level=os.getenv("NELA_LOG_LEVEL", "INFO"),
            data_dir=Path(os.getenv("NELA_DATA_DIR", "./data")),
            plugin_dir=Path(os.getenv("NELA_PLUGIN_DIR", "./plugins")),
            enable_voice=_env_bool("NELA_ENABLE_VOICE", default=False),
            enable_vision=_env_bool("NELA_ENABLE_VISION", default=False),
        )


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

