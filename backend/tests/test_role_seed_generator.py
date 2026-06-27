import json
from pathlib import Path

from scripts.generate_role_seed import build_roles, parse_catalog


def test_role_seed_matches_permission_catalog():
    backend_dir = Path(__file__).resolve().parents[1]
    catalog = backend_dir.parent / "docs" / "backend-permissions.md"
    seed = backend_dir / "seeds" / "roles.base.json"

    expected = build_roles(parse_catalog(catalog))
    assert json.loads(seed.read_text()) == expected


def test_role_seed_contains_system_and_module_roles():
    backend_dir = Path(__file__).resolve().parents[1]
    roles = {role["nombre"]: role for role in json.loads((backend_dir / "seeds" / "roles.base.json").read_text())}

    assert roles["SUPER_ADMIN"]["permisos"] == ["*"]
    assert "ventas.crear" in roles["ADMIN_EMPRESA"]["permisos"]
    assert "ventas.crear" in roles["VENTAS_CAJA"]["permisos"]
    assert "inventario.leer" in roles["INVENTARIO"]["permisos"]
