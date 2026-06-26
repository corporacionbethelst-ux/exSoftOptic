#!/usr/bin/env python3
"""Validate runtime environment safety before deploying the backend."""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from urllib.parse import urlparse


DEFAULT_INSECURE_SECRETS = {
    "tu_secret_key_super_seguro_cambiar_en_produccion_2026",
    "test_secret_key_change_me",
    "change-me",
    "secret",
}


@dataclass(frozen=True)
class Finding:
    level: str
    message: str


class RuntimeConfigValidator:
    def __init__(self, *, environment: str, strict: bool) -> None:
        self.environment = environment.lower()
        self.strict = strict
        self.findings: list[Finding] = []

    def validate(self) -> list[Finding]:
        self._validate_required("SECRET_KEY")
        self._validate_required("DATABASE_URL")
        self._validate_required("REDIS_URL")
        self._validate_database_url()
        self._validate_secret_strength()
        self._validate_provider("CFDI", default_allowed={"development", "test", "local"})
        self._validate_provider("BANKING", default_allowed={"development", "test", "local"})
        self._validate_cors()
        return self.findings

    def _validate_required(self, key: str) -> None:
        if not os.getenv(key):
            self._error(f"{key} es obligatorio")

    def _validate_database_url(self) -> None:
        database_url = os.getenv("DATABASE_URL", "")
        if database_url and not database_url.startswith("postgresql+asyncpg://"):
            self._error("DATABASE_URL debe usar postgresql+asyncpg://")

    def _validate_secret_strength(self) -> None:
        secret = os.getenv("SECRET_KEY", "")
        if secret in DEFAULT_INSECURE_SECRETS:
            self._error("SECRET_KEY usa un valor inseguro de ejemplo")
        if self._is_production() and len(secret) < 32:
            self._error("SECRET_KEY debe tener al menos 32 caracteres en producción")

    def _validate_provider(self, prefix: str, *, default_allowed: set[str]) -> None:
        provider = os.getenv(f"{prefix}_PROVIDER", "").upper()
        api_url = os.getenv(f"{prefix}_API_URL", "")
        api_key = os.getenv(f"{prefix}_API_KEY", "")
        timeout = os.getenv(f"{prefix}_TIMEOUT_SECONDS", "")
        if provider in {"HTTP", "API"}:
            if not api_url:
                self._error(f"{prefix}_API_URL es obligatorio cuando {prefix}_PROVIDER={provider}")
            if not api_key:
                self._error(f"{prefix}_API_KEY es obligatorio cuando {prefix}_PROVIDER={provider}")
        if provider in {"MOCK", "CSV"} and self.environment not in default_allowed:
            self._error(f"{prefix}_PROVIDER={provider} no debe usarse en {self.environment}")
        if timeout:
            try:
                if float(timeout) <= 0:
                    self._error(f"{prefix}_TIMEOUT_SECONDS debe ser mayor que cero")
            except ValueError:
                self._error(f"{prefix}_TIMEOUT_SECONDS debe ser numérico")
        if api_url:
            parsed = urlparse(api_url)
            if self._is_production() and parsed.scheme != "https":
                self._error(f"{prefix}_API_URL debe usar HTTPS en producción")

    def _validate_cors(self) -> None:
        cors_origins = os.getenv("CORS_ORIGINS", "")
        if self._is_production() and ("*" in cors_origins or "localhost" in cors_origins):
            self._error("CORS_ORIGINS no debe permitir '*' ni localhost en producción")

    def _is_production(self) -> bool:
        return self.environment in {"production", "prod"}

    def _error(self, message: str) -> None:
        self.findings.append(Finding("ERROR", message))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate backend runtime environment configuration")
    parser.add_argument("--environment", default=os.getenv("ENVIRONMENT", "development"))
    parser.add_argument("--strict", action="store_true", help="Treat warnings as deployment-blocking findings")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = RuntimeConfigValidator(environment=args.environment, strict=args.strict).validate()
    errors = [finding for finding in findings if finding.level == "ERROR"]
    for finding in findings:
        print(f"{finding.level}: {finding.message}")
    if errors:
        print(f"❌ runtime config validation failed with {len(errors)} error(s)")
        return 1
    print("✅ runtime config validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
