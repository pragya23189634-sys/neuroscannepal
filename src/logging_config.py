"""Central logging setup for NeuroScan Nepal backend and pipeline."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class _ColourFormatter(logging.Formatter):
    COLOURS = {
        logging.DEBUG: "\033[36m",
        logging.INFO: "\033[32m",
        logging.WARNING: "\033[33m",
        logging.ERROR: "\033[31m",
        logging.CRITICAL: "\033[41m",
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        colour = self.COLOURS.get(record.levelno, "")
        message = super().format(record)
        if colour and sys.stdout.isatty():
            return f"{colour}{message}{self.RESET}"
        return message


def setup_logging(
    log_dir: Path | None = None,
    log_name: str = "neuroscan",
    level: str | None = None,
) -> logging.Logger:
    """Configure root neuroscan logger with terminal + rotating file output."""
    resolved_level = getattr(logging, (level or os.getenv("NEUROSCAN_LOG_LEVEL", "INFO")).upper(), logging.INFO)
    logger = logging.getLogger(log_name)
    logger.setLevel(resolved_level)
    logger.propagate = False

    if logger.handlers:
        return logger

    if log_dir is None:
        log_dir = Path.cwd()
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / f"{log_name}.log"

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(_ColourFormatter(LOG_FORMAT, DATE_FORMAT))

    file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))

    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.info("Logging initialized | level=%s | file=%s", logging.getLevelName(resolved_level), log_path)
    return logger


def get_logger(name: str) -> logging.Logger:
    parent = logging.getLogger("neuroscan")
    if not parent.handlers:
        setup_logging()
    return parent.getChild(name)
