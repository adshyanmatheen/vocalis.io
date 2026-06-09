from __future__ import annotations

import subprocess
from pathlib import Path


def main() -> None:
    backend_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        [str(backend_root / ".venv" / "bin" / "alembic"), "upgrade", "head"],
        cwd=backend_root,
        check=True,
    )


if __name__ == "__main__":
    main()
