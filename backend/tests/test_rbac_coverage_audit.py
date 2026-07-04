from pathlib import Path

from scripts.audit_rbac_coverage import PERMISSION_PATTERN, RbacFinding, audit_rbac_coverage, flatten_permissions


def test_rbac_coverage_audit_passes_current_catalog_and_roles():
    assert audit_rbac_coverage() == []


def test_rbac_permission_naming_convention_requires_module_and_action():
    assert PERMISSION_PATTERN.match("ventas.crear")
    assert PERMISSION_PATTERN.match("configuracion.series.usar")
    assert not PERMISSION_PATTERN.match("Ventas.crear")
    assert not PERMISSION_PATTERN.match("ventas")


def test_rbac_audit_detects_unknown_role_permission(tmp_path: Path):
    endpoints_dir = tmp_path / "endpoints"
    endpoints_dir.mkdir()
    (endpoints_dir / "ventas.py").write_text('from app.api.deps import require_permissions\nDepends(require_permissions(["ventas.crear"]))')
    catalog = tmp_path / "backend-permissions.md"
    catalog.write_text("# Backend permission catalog\n\n## ventas\n\n- `ventas.crear`\n")
    roles = tmp_path / "roles.base.json"
    roles.write_text('[{"nombre":"ADMIN_EMPRESA","permisos":["ventas.crear","ventas.borrar"]}]')

    findings = audit_rbac_coverage(endpoints_dir=endpoints_dir, catalog_path=catalog, role_seed_path=roles)

    assert RbacFinding("role-unknown-permission", "Role `ADMIN_EMPRESA` references unknown permission `ventas.borrar`.") in findings


def test_flatten_permissions_accepts_sets_and_lists():
    assert flatten_permissions({"ventas": {"ventas.crear"}, "reportes": ["reportes.leer"]}) == {"ventas.crear", "reportes.leer"}
