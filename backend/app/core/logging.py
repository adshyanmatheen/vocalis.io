from __future__ import annotations

import logging
import sys

from app.core.config import settings


def configure_logging() -> None:
    if settings.app.environment == "production":
        from pythonjsonlogger import jsonlogger

        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            jsonlogger.JsonFormatter(
                "%(asctime)s %(levelname)s %(name)s %(message)s",
            )
        )
        logging.basicConfig(
            level=settings.app.log_level,
            handlers=[handler],
            force=True,
        )
    else:
        logging.basicConfig(
            level=settings.app.log_level,
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            stream=sys.stdout,
            force=True,
        )
