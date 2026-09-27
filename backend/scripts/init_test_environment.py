#!/usr/bin/env python3
"""Initialize local backend test environment files without overwriting secrets."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEMPLATE = BACKEND_ROOT / ".env.test.example"
DEFAULT_OUTPUT = BACKEND_ROOT / ".env.test.local"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true", help="Overwrite the output file when it already exists.")
    return parser.parse_args()


def init_env_file(*, template: Path = DEFAULT_TEMPLATE, output: Path = DEFAULT_OUTPUT, force: bool = False) -> str:
    if not template.exists():
        raise FileNotFoundError(f"Template not found: {template}")
    if output.exists() and not force:
        return f"kept existing {output}"
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, output)
    return f"wrote {output} from {template}"


def main() -> int:
    args = parse_args()
    message = init_env_file(template=args.template, output=args.output, force=args.force)
    print(message)
    print("Next: review the env file, then run `make test-services-up` and `make test-services-wait`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
