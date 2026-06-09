from __future__ import annotations

import asyncio
import logging
import sqlite3
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def _get_database_file_path() -> Path:
    raw_url = settings.app.database_url
    sqlite_prefix = "sqlite+aiosqlite:///"
    if not raw_url.startswith(sqlite_prefix):
        raise RuntimeError(f"Unsupported database URL scheme: {raw_url}")
    return Path(raw_url.removeprefix(sqlite_prefix))


def _get_backup_dir() -> Path:
    db_path = _get_database_file_path()
    return db_path.parent / settings.app.backup_directory


def create_database_backup() -> Path:
    db_path = _get_database_file_path()
    backup_dir = _get_backup_dir()
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"vocalis_{timestamp}.db"

    source_conn: sqlite3.Connection | None = None
    dest_conn: sqlite3.Connection | None = None
    try:
        source_conn = sqlite3.connect(str(db_path))
        dest_conn = sqlite3.connect(str(backup_path))
        with dest_conn:
            source_conn.backup(dest_conn, pages=-1)
        logger.info(
            "Database backup created: %s (%.1f MB)",
            backup_path,
            backup_path.stat().st_size / (1024 * 1024),
        )
    finally:
        if source_conn:
            source_conn.close()
        if dest_conn:
            dest_conn.close()

    _prune_old_backups(backup_dir)

    return backup_path


def _prune_old_backups(backup_dir: Path) -> None:
    retention_days = settings.app.backup_retention_days
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    removed: list[str] = []

    for backup_file in _get_backup_files(backup_dir):
        mtime = datetime.fromtimestamp(backup_file.stat().st_mtime, tz=UTC)
        if mtime < cutoff:
            backup_file.unlink()
            removed.append(backup_file.name)

    if removed:
        logger.info("Pruned %d old backup(s): %s", len(removed), ", ".join(removed))


async def create_database_backup_async() -> Path | None:
    if not settings.app.backup_enabled:
        logger.info("Database backup skipped (backup_enabled=False)")
        return None
    return await asyncio.to_thread(create_database_backup)


def _get_backup_files(backup_dir: Path) -> Sequence[Path]:
    if not backup_dir.is_dir():
        return []
    return sorted(
        p
        for p in backup_dir.iterdir()
        if p.suffix == ".db" and p.stem.startswith("vocalis_")
    )
