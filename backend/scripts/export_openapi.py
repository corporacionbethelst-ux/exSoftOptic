#!/usr/bin/env python3
"""Export the FastAPI OpenAPI contract to a JSON artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export backend OpenAPI schema")
    parser.add_argument("--output", type=Path, default=Path("../docs/openapi.json"))
    return parser.parse_args()


def main() -> int:
    from app.main import app

    args = parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(f"✅ OpenAPI contract exported to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
