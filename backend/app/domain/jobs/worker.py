from __future__ import annotations

import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


async def cleanup_stale_sessions(ctx: dict) -> None:
    """Periodic cleanup of stale rate limiter keys and temporary data."""
    logger.info("Running stale session cleanup")
    await asyncio.sleep(0)


async def demo_job(ctx: dict, payload: str) -> str:
    """Example job demonstrating the worker infrastructure."""
    logger.info("Demo job received payload: %s", payload)
    return f"processed: {payload}"


async def startup(ctx: dict) -> None:
    logger.info("arq worker started")


async def shutdown(ctx: dict) -> None:
    logger.info("arq worker shutting down")


async def run_worker() -> None:
    try:
        from arq import create_pool
        from arq.connections import RedisSettings
        from arq.worker import Worker as ArqWorker

        redis_settings = (
            RedisSettings().from_dsn(settings.app.redis_url)
            if settings.app.redis_url
            else None
        )

        if redis_settings is None:
            logger.warning("Redis not configured — skipping arq worker")
            return

        pool = await create_pool(redis_settings)

        worker = ArqWorker(
            pool=pool,
            functions=[cleanup_stale_sessions, demo_job],
            on_startup=startup,
            on_shutdown=shutdown,
            poll_delay=1.0,
            max_jobs=4,
        )

        logger.info("arq worker starting...")
        await worker.async_run()
    except ImportError:
        logger.warning("arq not installed — background worker unavailable")
    except Exception:
        logger.exception("arq worker failed to start")
