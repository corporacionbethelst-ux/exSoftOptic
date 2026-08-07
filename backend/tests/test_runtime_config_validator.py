from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

from scripts.validate_runtime_config import RuntimeConfigValidator


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_runtime_config.py"


PRODUCTION_ENV = {
    "SECRET_KEY": "a" * 48,
    "DATABASE_URL": "postgresql+asyncpg://user:secure@postgres:5432/app",
    "MONGODB_URL": "mongodb://user:secure@mongodb:27017/app",
    "REDIS_URL": "redis://redis:6379/0",
    "DEBUG": "false",
    "ALGORITHM": "HS256",
    "CORS_ORIGINS": '["https://app.optica.example"]',
    "CFDI_PROVIDER": "HTTP",
    "CFDI_API_URL": "https://cfdi.example/api",
    "CFDI_API_KEY": "secure-cfdi-key",
    "BANKING_PROVIDER": "HTTP",
    "BANKING_API_URL": "https://bank.example/api",
    "BANKING_API_KEY": "secure-bank-key",
}


def validate(overrides: dict[str, str] | None = None) -> list[str]:
    environment = PRODUCTION_ENV | (overrides or {})
    with patch.dict(os.environ, environment, clear=True):
        findings = RuntimeConfigValidator(environment="production", strict=True).validate()
    return [finding.message for finding in findings]


def test_accepts_hardened_production_configuration() -> None:
    assert validate() == []


def test_rejects_debug_and_local_service_endpoints() -> None:
    messages = validate(
        {
            "DEBUG": "true",
            "REDIS_URL": "redis://localhost:6379/0",
            "MONGODB_URL": "mongodb://user:change-me@mongodb:27017/app",
        }
    )
    assert "DEBUG debe estar deshabilitado en producción" in messages
    assert "REDIS_URL no debe apuntar a localhost en producción" in messages
    assert "MONGODB_URL contiene credenciales o valores de ejemplo" in messages


def test_rejects_unsupported_jwt_algorithm() -> None:
    assert "ALGORITHM debe ser HS256, HS384 o HS512" in validate({"ALGORITHM": "none"})


def test_rejects_placeholder_provider_credentials() -> None:
    messages = validate({"CFDI_API_KEY": "replace-with-secret-manager-reference"})
    assert "CFDI_API_KEY contiene un valor de ejemplo" in messages


def run_validator(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    merged_env.update(env)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--environment", env.get("ENVIRONMENT", "test")],
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_passes_for_test_defaults() -> None:
    result = run_validator(
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


def test_cli_rejects_unsafe_production_defaults() -> None:
    result = run_validator(
        {
            "ENVIRONMENT": "production",
            "DEBUG": "true",
            "SECRET_KEY": "secret",
            "DATABASE_URL": "postgresql://user:password_2026@localhost:5432/db",
            "REDIS_URL": "redis://localhost:6379/0",
            "CFDI_PROVIDER": "MOCK",
            "BANKING_PROVIDER": "CSV",
            "CORS_ORIGINS": '["http://localhost:3000"]',
        }
    )
    assert result.returncode == 1
    assert "SECRET_KEY usa un valor inseguro" in result.stdout
    assert "DATABASE_URL debe usar postgresql+asyncpg://" in result.stdout
    assert "DEBUG debe estar deshabilitado" in result.stdout
    assert "CORS_ORIGINS" in result.stdout


def test_cli_accepts_secure_http_provider_configuration() -> None:
    result = run_validator(PRODUCTION_ENV | {"ENVIRONMENT": "production"})
    assert result.returncode == 0, result.stdout
