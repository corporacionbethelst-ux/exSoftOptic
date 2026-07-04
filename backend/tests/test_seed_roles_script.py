import json
from pathlib import Path

from scripts.seed_roles import load_role_seed


def test_load_role_seed_normalizes_permissions(tmp_path: Path):
    seed = tmp_path / "roles.json"
    seed.write_text(json.dumps([{"nombre": "TEST", "descripcion": "Role", "permisos": ["z", "a"], "nivel_acceso": "7"}]))

    roles = load_role_seed(seed)

    assert roles[0].nombre == "TEST"
    assert roles[0].permisos == ["a", "z"]
    assert roles[0].nivel_acceso == 7


def test_seed_roles_defers_database_imports_until_runtime():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "seed_roles.py").read_text()

    assert "from app.core.database import async_session_maker" in source
    assert "async def import_roles" in source
    assert "--dry-run" in source
