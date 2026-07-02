from pathlib import Path


def test_alembic_env_imports_registered_models_without_silent_import_guards():
    env_py = Path(__file__).resolve().parents[1] / "alembic" / "env.py"
    content = env_py.read_text(encoding="utf-8")

    assert "except ImportError" not in content
    assert "from app.models import (" in content
    for module_name in [
        "auditoria",
        "compra",
        "configuracion",
        "contabilidad",
        "crm",
        "empresa",
        "factura",
        "garantia",
        "idempotencia",
        "inventario",
        "laboratorio",
        "nomina",
        "outbox",
        "presupuesto",
        "producto",
        "sucursal",
        "tesoreria",
        "usuario",
        "venta",
    ]:
        assert f"    {module_name}," in content
