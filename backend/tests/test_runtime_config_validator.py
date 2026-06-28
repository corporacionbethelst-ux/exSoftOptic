import os
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_runtime_config.py"


def _run_validator(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--environment", env.get("ENVIRONMENT", "test")],
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_runtime_config_validator_passes_for_test_defaults():
    result = _run_validator(
        {
            "ENVIRONMENT": "test",
            "SECRET_KEY": "test_secret_key_that_is_long_enough",
            "DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/db",
            "REDIS_URL": "redis://localhost:6379/0",
            "CFDI_PROVIDER": "MOCK",
            "BANKING_PROVIDER": "CSV",
        }
    )

    assert result.returncode == 0
    assert "runtime config validation passed" in result.stdout


def test_runtime_config_validator_rejects_unsafe_production_defaults():
    result = _run_validator(
        {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "secret",
            "DATABASE_URL": "postgresql://user:pass@localhost:5432/db",
            "REDIS_URL": "redis://localhost:6379/0",
            "CFDI_PROVIDER": "MOCK",
            "BANKING_PROVIDER": "CSV",
            "CORS_ORIGINS": '["http://localhost:3000"]',
        }
    )

    assert result.returncode == 1
    assert "SECRET_KEY usa un valor inseguro" in result.stdout
    assert "DATABASE_URL debe usar postgresql+asyncpg://" in result.stdout
    assert "CORS_ORIGINS" in result.stdout


def test_runtime_config_validator_requires_http_provider_credentials():
    result = _run_validator(
        {
            "ENVIRONMENT": "production",
            "SECRET_KEY": "prod_secret_key_that_is_safely_long_enough",
            "DATABASE_URL": "postgresql+asyncpg://user:pass@db:5432/db",
            "REDIS_URL": "redis://redis:6379/0",
            "CFDI_PROVIDER": "HTTP",
            "CFDI_API_URL": "https://cfdi.example",
            "CFDI_API_KEY": "cfdi-key",
            "BANKING_PROVIDER": "HTTP",
            "BANKING_API_URL": "https://bank.example",
            "BANKING_API_KEY": "bank-key",
            "CORS_ORIGINS": '["https://app.example"]',
        }
    )

    assert result.returncode == 0
