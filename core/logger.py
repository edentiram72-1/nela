"""Centralized logging configuration."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILES = {
    "nela.brain": "brain.log",
    "nela.voice": "voice.log",
    "nela.agents": "agents.log",
    "nela.errors": "errors.log",
    "nela.performance": "performance.log",
}


def configure_logging(log_dir: Path | str = "logs", level: str = "INFO") -> None:
    """Configure root and module-specific loggers."""

    target_dir = Path(log_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    for logger_name, filename in LOG_FILES.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        if _has_file_handler(logger, target_dir / filename):
            continue
        handler = RotatingFileHandler(
            target_dir / filename,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)


def _has_file_handler(logger: logging.Logger, path: Path) -> bool:
    return any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename) == path.resolve()
        for handler in logger.handlers
    )

