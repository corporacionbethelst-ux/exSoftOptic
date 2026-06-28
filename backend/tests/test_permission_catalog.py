from pathlib import Path

from scripts.generate_permission_catalog import collect_permissions, render_markdown


def test_permission_catalog_collects_endpoint_permissions():
    permissions = collect_permissions(Path("app/api/v1/endpoints"))

    assert "ventas" in permissions
    assert "ventas.crear" in permissions["ventas"]
    assert "observabilidad" in permissions
    assert "observabilidad.metricas.leer" in permissions["observabilidad"]


def test_permission_catalog_document_is_current():
    rendered = render_markdown(collect_permissions(Path("app/api/v1/endpoints")))
    current = (Path(__file__).resolve().parents[2] / "docs" / "backend-permissions.md").read_text()

    assert current == rendered
