#!/usr/bin/env python3
"""Validate runtime environment safety before deploying the backend."""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


BACKEND_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_FILES = (
    BACKEND_ROOT.parent / ".env",
    BACKEND_ROOT / ".env",
    BACKEND_ROOT / ".env.local",
)


DEFAULT_INSECURE_SECRETS = {
    "tu_secret_key_super_seguro_cambiar_en_produccion_2026",
    "test_secret_key_change_me",
    "change-me",
    "secret",
}

PLACEHOLDER_MARKERS = ("change-me", "tu_", "example", "password_2026")


def _strip_inline_comment(value: str) -> str:
    in_single = False
    in_double = False
    for index, char in enumerate(value):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return value[:index].rstrip()
    return value.strip()


def _clean_env_value(value: str) -> str:
    cleaned = _strip_inline_comment(value.strip())
    if len(cleaned) >= 2 and cleaned[0] == cleaned[-1] and cleaned[0] in {"'", '"'}:
        return cleaned[1:-1]
    return cleaned


def load_env_file(path: Path, *, override: bool = False) -> int:
    loaded = 0
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key or (key in os.environ and not override):
            continue
        os.environ[key] = _clean_env_value(value)
        loaded += 1
    return loaded


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
        self._validate_metrics_token()
        self._validate_release_metadata()
        self._validate_production_flags()
        self._validate_service_urls()
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
        if self._is_production() and "localhost" in database_url:
            self._error("DATABASE_URL no debe apuntar a localhost en producción")

    def _validate_secret_strength(self) -> None:
        secret = os.getenv("SECRET_KEY", "")
        if secret in DEFAULT_INSECURE_SECRETS or secret.startswith("change-me"):
            self._error("SECRET_KEY usa un valor inseguro de ejemplo")
        if self._is_production() and len(secret) < 32:
            self._error("SECRET_KEY debe tener al menos 32 caracteres en producción")

    def _validate_production_flags(self) -> None:
        debug = os.getenv("DEBUG", "false").strip().lower()
        if self._is_production() and debug not in {"false", "0", "no", "off"}:
            self._error("DEBUG debe estar deshabilitado en producción")
        algorithm = os.getenv("ALGORITHM", "HS256").upper()
        if algorithm not in {"HS256", "HS384", "HS512"}:
            self._error("ALGORITHM debe ser HS256, HS384 o HS512")

    def _validate_metrics_token(self) -> None:
        token = os.getenv("METRICS_TOKEN", "")
        if self._is_production() and len(token) < 32:
            self._error("METRICS_TOKEN debe tener al menos 32 caracteres en producción")
        if token and any(marker in token.lower() for marker in PLACEHOLDER_MARKERS):
            self._error("METRICS_TOKEN contiene un valor de ejemplo")

    def _validate_release_metadata(self) -> None:
        if not self._is_production():
            return
        release_sha = os.getenv("RELEASE_SHA", "")
        deployed_at = os.getenv("DEPLOYED_AT", "")
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", release_sha):
            self._error("RELEASE_SHA debe contener el hash hexadecimal del release")
        if not deployed_at or deployed_at in {"unknown", "replace-at-deploy"}:
            self._error("DEPLOYED_AT debe identificar la fecha del despliegue")

    def _validate_service_urls(self) -> None:
        if not self._is_production():
            return
        for key in ("DATABASE_URL", "MONGODB_URL", "REDIS_URL"):
            value = os.getenv(key, "")
            lowered = value.lower()
            if "localhost" in lowered or "127.0.0.1" in lowered:
                self._error(f"{key} no debe apuntar a localhost en producción")
            if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
                self._error(f"{key} contiene credenciales o valores de ejemplo")

    def _validate_provider(self, prefix: str, *, default_allowed: set[str]) -> None:
        provider = os.getenv(f"{prefix}_PROVIDER", "").upper()
        api_url = os.getenv(f"{prefix}_API_URL", "")
        api_key = os.getenv(f"{prefix}_API_KEY", "")
        timeout = os.getenv(f"{prefix}_TIMEOUT_SECONDS", "")
        retry_attempts = os.getenv(f"{prefix}_RETRY_ATTEMPTS", "")
        circuit_threshold = os.getenv(f"{prefix}_CIRCUIT_FAILURE_THRESHOLD", "")
        circuit_recovery = os.getenv(f"{prefix}_CIRCUIT_RECOVERY_SECONDS", "")
        if provider in {"HTTP", "API"}:
            if not api_url:
                self._error(f"{prefix}_API_URL es obligatorio cuando {prefix}_PROVIDER={provider}")
            if not api_key:
                self._error(f"{prefix}_API_KEY es obligatorio cuando {prefix}_PROVIDER={provider}")
            elif self._is_production() and any(
                marker in api_key.lower()
                for marker in (*PLACEHOLDER_MARKERS, "replace-with")
            ):
                self._error(f"{prefix}_API_KEY contiene un valor de ejemplo")
        if provider in {"MOCK", "CSV"} and self.environment not in default_allowed:
            self._error(f"{prefix}_PROVIDER={provider} no debe usarse en {self.environment}")
        if timeout:
            try:
                if float(timeout) <= 0:
                    self._error(f"{prefix}_TIMEOUT_SECONDS debe ser mayor que cero")
            except ValueError:
                self._error(f"{prefix}_TIMEOUT_SECONDS debe ser numérico")
        if retry_attempts:
            try:
                if int(retry_attempts) < 1:
                    self._error(f"{prefix}_RETRY_ATTEMPTS debe ser mayor que cero")
            except ValueError:
                self._error(f"{prefix}_RETRY_ATTEMPTS debe ser numérico")
        if circuit_threshold:
            try:
                if int(circuit_threshold) < 1:
                    self._error(f"{prefix}_CIRCUIT_FAILURE_THRESHOLD debe ser mayor que cero")
            except ValueError:
                self._error(f"{prefix}_CIRCUIT_FAILURE_THRESHOLD debe ser numérico")
        if circuit_recovery:
            try:
                if float(circuit_recovery) < 0:
                    self._error(f"{prefix}_CIRCUIT_RECOVERY_SECONDS no puede ser negativo")
            except ValueError:
                self._error(f"{prefix}_CIRCUIT_RECOVERY_SECONDS debe ser numérico")
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
    parser = argparse.ArgumentParser(
        description="Validate backend runtime environment configuration"
    )
    parser.add_argument("--environment", default=None)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as deployment-blocking findings",
    )
    parser.add_argument(
        "--env-file",
        action="append",
        type=Path,
        default=[],
        help="Archivo .env a cargar antes de validar; puede repetirse",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_files = args.env_file or [path for path in DEFAULT_ENV_FILES if path.exists()]
    for env_file in env_files:
        load_env_file(env_file)

    environment = args.environment or os.getenv("ENVIRONMENT", "development")
    findings = RuntimeConfigValidator(environment=environment, strict=args.strict).validate()
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
