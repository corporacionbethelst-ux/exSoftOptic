from pathlib import Path

from scripts.check_test_readiness import CRITICAL_REQUIREMENTS, run_checks


def test_test_readiness_knows_critical_backend_test_dependencies():
    assert {"fastapi", "sqlalchemy", "asyncpg", "httpx", "pytest", "pytest-asyncio"}.issubset(CRITICAL_REQUIREMENTS)


def test_test_readiness_script_uses_only_stdlib_imports():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "check_test_readiness.py").read_text()

    assert "from app." not in source
    assert "import fastapi" not in source
    assert "import sqlalchemy" not in source


def test_test_readiness_has_no_blockers_for_repository_shape():
    blockers = [result for result in run_checks() if result.blocking and not result.ok]

    assert blockers == []
