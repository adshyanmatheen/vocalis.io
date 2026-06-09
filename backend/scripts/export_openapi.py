from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import msgspec

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.main import app  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export the backend OpenAPI contract.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("openapi.json"),
        help="Path to write the OpenAPI JSON contract.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    contract = msgspec.to_builtins(app.openapi_schema)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(contract, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
