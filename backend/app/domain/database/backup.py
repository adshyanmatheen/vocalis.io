from __future__ import annotations

import asyncio
import logging
import sqlite3
import subprocess
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)

BACKUP_FILENAME_PREFIX = "vocalis"
BACKUP_EXTENSION = ".db"


def _get_postgres_connection_params(database_url: str) -> dict[str, str]:
    parsed = urlparse(database_url)
    return {
        "host": parsed.hostname or "localhost",
        "port": str(parsed.port or 5432),
        "dbname": parsed.path.lstrip("/"),
        "user": parsed.username or "vocalis",
        "password": parsed.password or "",
    }


def create_database_backup(
    *,
    override_database_url: str | None = None,
    override_backup_dir: str | None = None,
) -> Path:
    return _create_database_backup(
        database_url=override_database_url or settings.app.database_url,
        backup_dir=override_backup_dir or settings.app.backup_directory,
    )


def _create_database_backup(*, database_url: str, backup_dir: str) -> Path:
    _backup_dir = _resolve_backup_dir(database_url, backup_dir)
    _backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    backup_path = (
        _backup_dir / f"{BACKUP_FILENAME_PREFIX}_{timestamp}{BACKUP_EXTENSION}"
    )

    if database_url.startswith("sqlite"):
        _backup_sqlite(database_url, backup_path)
    else:
        _backup_postgres(database_url, backup_path)

    _prune_old_backups(_backup_dir)

    return backup_path


def _resolve_backup_dir(database_url: str, backup_dir: str) -> Path:
    if database_url.startswith("sqlite"):
        sqlite_prefix = "sqlite+aiosqlite:///"
        db_path = Path(database_url.removeprefix(sqlite_prefix))
        return db_path.parent / backup_dir
    return Path(backup_dir)


def _backup_sqlite(database_url: str, backup_path: Path) -> None:
    sqlite_prefix = "sqlite+aiosqlite:///"
    db_path = Path(database_url.removeprefix(sqlite_prefix))

    source_conn: sqlite3.Connection | None = None
    dest_conn: sqlite3.Connection | None = None
    try:
        source_conn = sqlite3.connect(str(db_path))
        dest_conn = sqlite3.connect(str(backup_path))
        with dest_conn:
            source_conn.backup(dest_conn, pages=-1)
        logger.info(
            "SQLite backup created: %s (%.1f MB)",
            backup_path,
            backup_path.stat().st_size / (1024 * 1024),
        )
    finally:
        if source_conn:
            source_conn.close()
        if dest_conn:
            dest_conn.close()


def _backup_postgres(database_url: str, backup_path: str | Path) -> None:
    params = _get_postgres_connection_params(database_url)
    env = {**__import__("os").environ, "PGPASSWORD": params["password"]}
    cmd = [
        "pg_dump",
        "--host",
        params["host"],
        "--port",
        params["port"],
        "--username",
        params["user"],
        "--dbname",
        params["dbname"],
        "--format",
        "custom",
        "--file",
        str(backup_path),
        "--no-owner",
        "--no-acl",
    ]

    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            logger.error("pg_dump failed: %s", result.stderr)
            raise RuntimeError(f"pg_dump failed: {result.stderr}")
        logger.info(
            "PostgreSQL backup created: %s (%.1f MB)",
            backup_path,
            Path(backup_path).stat().st_size / (1024 * 1024),
        )
    except FileNotFoundError:
        logger.warning("pg_dump not found — skipping PostgreSQL backup")


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
        if p.suffix == ".db" and p.stem.startswith(BACKUP_FILENAME_PREFIX + "_")
    )
