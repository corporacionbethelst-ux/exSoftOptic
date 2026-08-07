from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "init_production_environment.py"
SPEC = importlib.util.spec_from_file_location("init_production_environment", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def parse_env(content: str) -> dict[str, str]:
    return {
        key: value
        for line in content.splitlines()
        if line and not line.startswith("#") and "=" in line
        for key, value in [line.split("=", 1)]
    }


def test_render_creates_distinct_secrets_and_authenticated_service_urls() -> None:
    first = parse_env(
        MODULE.render(
            domain="app.example.com",
            postgres_host="postgres",
            mongo_host="mongodb",
            redis_host="redis",
        )
    )
    second = parse_env(
        MODULE.render(
            domain="app.example.com",
            postgres_host="postgres",
            mongo_host="mongodb",
            redis_host="redis",
        )
    )

    assert first["ENVIRONMENT"] == "production"
    assert first["DEBUG"] == "false"
    assert first["CORS_ORIGINS"] == '["https://app.example.com"]'
    assert first["REDIS_PASSWORD"] in first["REDIS_URL"]
    assert first["OPTICA_POSTGRES_PASSWORD"] != second["OPTICA_POSTGRES_PASSWORD"]
    assert first["OPTICA_MONGO_PASSWORD"] != second["OPTICA_MONGO_PASSWORD"]
    assert first["REDIS_PASSWORD"] != second["REDIS_PASSWORD"]
    assert first["SECRET_KEY"] != second["SECRET_KEY"]
    assert len(first["SECRET_KEY"]) >= 64
