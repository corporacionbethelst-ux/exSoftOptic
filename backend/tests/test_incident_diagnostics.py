import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "collect_incident_diagnostics.py"
SPEC = importlib.util.spec_from_file_location("collect_incident_diagnostics", SCRIPT)
assert SPEC and SPEC.loader
diagnostics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(diagnostics)


def test_collect_excludes_environment_and_logs(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(diagnostics, "ROOT", tmp_path)
    monkeypatch.setattr(
        diagnostics,
        "run",
        lambda command, **kwargs: {"available": True, "returncode": 0, "stdout": "ok", "stderr": ""},
    )
    monkeypatch.setattr(
        diagnostics,
        "probe",
        lambda url, **kwargs: {"status": 200, "latency_ms": 1.0, "body": {"status": "ok"}},
    )
    payload = diagnostics.collect(base_url="https://example.com", include_docker=True)
    assert "environment" not in payload
    assert "logs" not in payload
    assert payload["health"]["status"] == 200
    assert payload["readiness"]["status"] == 200
    assert "docker_compose_ps" in payload


def test_run_does_not_include_command_environment(tmp_path: Path):
    result = diagnostics.run(["python3", "-c", "print('safe')"], cwd=tmp_path)
    assert result["returncode"] == 0
    assert result["stdout"] == "safe"
    assert set(result) == {"available", "returncode", "stdout", "stderr"}
