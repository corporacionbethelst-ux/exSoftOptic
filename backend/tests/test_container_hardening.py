from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]


def test_dockerfile_runs_as_non_root_and_has_healthcheck():
    dockerfile = (BACKEND_ROOT / "Dockerfile").read_text()

    assert "USER app" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "ENTRYPOINT" in dockerfile
    assert "--reload" not in dockerfile


def test_entrypoint_supports_explicit_migration_flag():
    entrypoint = (BACKEND_ROOT / "docker" / "entrypoint.sh").read_text()

    assert "RUN_MIGRATIONS_ON_START" in entrypoint
    assert "alembic upgrade head" in entrypoint
    assert 'exec "$@"' in entrypoint


def test_dockerignore_excludes_sensitive_runtime_artifacts():
    dockerignore = (BACKEND_ROOT / ".dockerignore").read_text()

    for pattern in [".env", "venv/", "backups/", "uploads/", "logs/", ".git/"]:
        assert pattern in dockerignore
