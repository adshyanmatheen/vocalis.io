from __future__ import annotations

import os
import sqlite3
from datetime import UTC, datetime, timedelta
from pathlib import Path

from app.domain.database.backup import (
    _get_backup_files,
    _prune_old_backups,
    create_database_backup,
)


class TestCreateDatabaseBackup:
    def test_creates_backup_file(self, tmp_path: Path) -> None:
        db_path = tmp_path / "vocalis.db"
        sqlite3.connect(str(db_path)).close()

        backup_path = create_database_backup(
            override_database_url=f"sqlite+aiosqlite:///{db_path}",
            override_backup_dir=str(tmp_path / "backups"),
        )
        assert backup_path.exists()
        assert backup_path.suffix == ".db"
        assert "vocalis_" in backup_path.stem

    def test_backup_is_valid_sqlite(self, tmp_path: Path) -> None:
        db_path = tmp_path / "vocalis.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO test VALUES (1)")
        conn.commit()
        conn.close()

        backup_path = create_database_backup(
            override_database_url=f"sqlite+aiosqlite:///{db_path}",
            override_backup_dir=str(tmp_path / "backups"),
        )
        backup_conn = sqlite3.connect(str(backup_path))
        cursor = backup_conn.execute("SELECT COUNT(*) FROM test")
        assert cursor.fetchone()[0] == 1
        backup_conn.close()

    def test_creates_backup_dir_if_not_exists(self, tmp_path: Path) -> None:
        db_path = tmp_path / "vocalis.db"
        sqlite3.connect(str(db_path)).close()

        backup_path = create_database_backup(
            override_database_url=f"sqlite+aiosqlite:///{db_path}",
            override_backup_dir=str(tmp_path / "backups"),
        )
        assert backup_path.parent.exists()
        assert backup_path.parent.is_dir()


class TestGetBackupFiles:
    def test_returns_empty_for_nonexistent_dir(self) -> None:
        assert _get_backup_files(Path("/nonexistent/path")) == []

    def test_only_returns_vocalis_backups(self, tmp_path: Path) -> None:
        (tmp_path / "vocalis_20260101_120000.db").touch()
        (tmp_path / "other.db").touch()
        files = _get_backup_files(tmp_path)
        assert len(files) == 1
        assert "vocalis_20260101_120000" in files[0].stem

    def test_returns_sorted(self, tmp_path: Path) -> None:
        (tmp_path / "vocalis_b.db").touch()
        (tmp_path / "vocalis_a.db").touch()
        files = _get_backup_files(tmp_path)
        assert len(files) == 2
        assert files[0].stem < files[1].stem


class TestPruneOldBackups:
    def test_removes_expired_backups(self, tmp_path: Path) -> None:
        old_file = tmp_path / "vocalis_old.db"
        old_file.touch()
        old_mtime = datetime.now(UTC) - timedelta(days=31)
        os.utime(str(old_file), (old_mtime.timestamp(), old_mtime.timestamp()))

        recent_file = tmp_path / "vocalis_recent.db"
        recent_file.touch()

        _prune_old_backups(tmp_path)
        assert not old_file.exists()
        assert recent_file.exists()

    def test_keeps_recent_backups(self, tmp_path: Path) -> None:
        recent_file = tmp_path / "vocalis_recent.db"
        recent_file.touch()

        _prune_old_backups(tmp_path)
        assert recent_file.exists()

    def test_removes_only_expired_backups(self, tmp_path: Path) -> None:
        old_file = tmp_path / "vocalis_old.db"
        old_file.touch()
        old_mtime = datetime.now(UTC) - timedelta(days=31)
        os.utime(str(old_file), (old_mtime.timestamp(), old_mtime.timestamp()))

        _prune_old_backups(tmp_path)
        assert not old_file.exists()
