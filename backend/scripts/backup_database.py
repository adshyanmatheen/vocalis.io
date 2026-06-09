from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.database.backup import create_database_backup


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a database backup.")
    return parser.parse_args()


def main() -> None:
    backup_path = create_database_backup()
    print(f"Backup created: {backup_path}")


if __name__ == "__main__":
    main()
