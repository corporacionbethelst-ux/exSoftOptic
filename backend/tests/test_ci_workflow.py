from pathlib import Path


def test_backend_ci_workflow_runs_verifier_migrations_and_tests():
    workflow = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "backend-ci.yml"
    content = workflow.read_text(encoding="utf-8")

    assert "postgres:16" in content
    assert "python scripts/verify_backend.py --skip-pytest" in content
    assert "python scripts/audit_api_security.py" in content
    assert "python scripts/verify_migrations.py --roundtrip" in content
    assert "python scripts/verify_backend.py -- -q" in content
    assert "python -m pytest tests/test_e2e_smoke.py -q" in content
    assert "TEST_DATABASE_URL" in content


def test_makefile_exposes_backend_verification_targets():
    makefile = Path(__file__).resolve().parents[1] / "Makefile"
    content = makefile.read_text(encoding="utf-8")

    assert "verify-fast:" in content
    assert "verify:" in content
    assert "ci:" in content
    assert "e2e:" in content
    assert "migrate-verify:" in content
    assert "security-audit:" in content
    assert "python scripts/verify_backend.py" in content
    assert "python -m pytest tests/test_e2e_smoke.py -q" in content
    assert "python scripts/verify_migrations.py --roundtrip" in content
    assert "python scripts/audit_api_security.py" in content
