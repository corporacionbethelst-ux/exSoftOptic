from scripts.seed_test_data import build_seed


def test_build_seed_is_deterministic():
    first = build_seed()
    second = build_seed()

    assert first == second
    assert first.rfc == "XAXX010101000"
    assert first.producto_sku == "TEST-ARMAZON-001"
    assert first.username == "test.admin"


def test_seed_test_data_defers_database_imports_until_runtime():
    from pathlib import Path

    source = (Path(__file__).resolve().parents[1] / "scripts" / "seed_test_data.py").read_text()

    assert "from app.core.database import async_session_maker" in source
    assert "async def seed_test_data" in source
    assert "--dry-run" in source
