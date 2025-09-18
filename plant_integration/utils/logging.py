"""Logging utilities tailored for high-throughput recycling environments."""

from __future__ import annotations

import logging
from typing import Optional

_LOGGER: Optional[logging.Logger] = None


def get_logger(name: str = "sortient") -> logging.Logger:
    """Return a module-level logger configured with sensible defaults."""

    global _LOGGER
    if _LOGGER is None:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        )
        _LOGGER = logging.getLogger(name)
    return _LOGGER

