from pathlib import Path


def test_staging_compose_declares_controlled_runtime_services():
    compose = Path(__file__).resolve().parents[2] / "docker-compose.staging.yml"
    source = compose.read_text()

    assert "outbox-worker:" in source
    assert "migration-job:" in source
    assert 'RUN_MIGRATIONS_ON_START: "false"' in source
    assert "--reload" not in source
    assert "exsoftoptic-backend:staging" in source
