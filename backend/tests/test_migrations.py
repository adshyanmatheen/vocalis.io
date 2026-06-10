from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"


def test_all_migrations_apply() -> None:
    with tempfile.TemporaryDirectory(prefix="vocalis-migration-test-") as tmpdir:
        db_path = Path(tmpdir) / "test.sqlite3"
        env = os.environ.copy()
        env["DATABASE_URL"] = f"sqlite+aiosqlite:///{db_path}"
        env["ENVIRONMENT"] = "development"
        env["JWT_SECRET_KEY"] = "test-jwt-secret-key-with-at-least-thirty-two-bytes"

        result = subprocess.run(
            ["alembic", "-c", str(ALEMBIC_INI), "upgrade", "head"],
            cwd=BACKEND_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"alembic upgrade failed:\n{result.stdout}\n{result.stderr}"
        )
        assert db_path.exists()
        assert db_path.stat().st_size > 0
