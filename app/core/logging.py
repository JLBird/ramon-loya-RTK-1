"""
RTK-1 Structured Logging – JSON output for ELK/Loki, console for dev.
Import get_logger() everywhere instead of using print().
"""

import logging
import sys
from pathlib import Path
from typing import Any

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Call once at startup in main.py."""
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.log_format == "json":
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    # --- File sink for Loki/Alloy ingestion ---
    log_dir = Path("C:/Projects/RTK-1/ramon-loya-RTK-1/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = open(log_dir / "rtk1.log", "a", buffering=1, encoding="utf-8")

    class TeeLoggerFactory:
        """Write JSON logs to both stdout and file."""

        def __call__(self, *args):
            return structlog.PrintLogger(
                file=log_file if settings.log_format == "json" else sys.stdout
            )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=TeeLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to route through structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Mirror stdlib logs to file too
    if settings.log_format == "json":
        file_handler = logging.FileHandler(log_dir / "rtk1.log", encoding="utf-8")
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> Any:
    """Get a structured logger bound to a component name."""
    return structlog.get_logger(component=name)
