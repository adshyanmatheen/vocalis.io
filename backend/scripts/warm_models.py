from __future__ import annotations

import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from app.domain.models import (  # noqa: E402
    get_model_readiness_snapshot,
    warm_model_bundles,
)


def main() -> None:
    warm_model_bundles(download=True)
    print(json.dumps(get_model_readiness_snapshot(), indent=2))


if __name__ == "__main__":
    main()
