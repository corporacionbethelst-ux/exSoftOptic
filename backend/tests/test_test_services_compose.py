from pathlib import Path


def test_test_compose_uses_isolated_ephemeral_services():
    compose = Path(__file__).resolve().parents[2] / "docker-compose.test.yml"
    source = compose.read_text()

    assert "postgres-test:" in source
    assert "redis-test:" in source
    assert "mongodb-test:" in source
    assert "55432:5432" in source
    assert "56379:6379" in source
    assert "57017:27017" in source
    assert "tmpfs:" in source


def test_test_env_template_points_to_isolated_ports():
    env_template = Path(__file__).resolve().parents[1] / ".env.test.example"
    source = env_template.read_text()

    assert "ENVIRONMENT=test" in source
    assert "localhost:55432" in source
    assert "localhost:56379" in source
    assert "localhost:57017" in source
