#!/usr/bin/env python3
"""Audit consistency between endpoint permissions, permission catalog and role seed."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from scripts.generate_permission_catalog import collect_permissions
from scripts.generate_role_seed import parse_catalog

ENDPOINTS_DIR = Path("app/api/v1/endpoints")
CATALOG_PATH = Path("../docs/backend-permissions.md")
ROLE_SEED_PATH = Path("seeds/roles.base.json")
PERMISSION_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(?:\.[a-z][a-z0-9_]*)+$")


@dataclass(frozen=True)
class RbacFinding:
    code: str
    detail: str


def flatten_permissions(permissions_by_module: dict[str, list[str] | set[str]]) -> set[str]:
    return {permission for permissions in permissions_by_module.values() for permission in permissions}


def load_roles(path: Path = ROLE_SEED_PATH) -> list[dict]:
    return json.loads(path.read_text())


def audit_rbac_coverage(
    *,
    endpoints_dir: Path = ENDPOINTS_DIR,
    catalog_path: Path = CATALOG_PATH,
    role_seed_path: Path = ROLE_SEED_PATH,
) -> list[RbacFinding]:
    findings: list[RbacFinding] = []
    endpoint_permissions_by_module = collect_permissions(endpoints_dir)
    endpoint_permissions = flatten_permissions(endpoint_permissions_by_module)
    catalog_permissions_by_module = parse_catalog(catalog_path)
    catalog_permissions = flatten_permissions(catalog_permissions_by_module)
    roles = load_roles(role_seed_path)

    for permission in sorted(endpoint_permissions):
        if not PERMISSION_PATTERN.match(permission):
            findings.append(RbacFinding("invalid-permission-name", f"Endpoint permission `{permission}` does not match RBAC naming convention."))

    missing_from_catalog = endpoint_permissions - catalog_permissions
    for permission in sorted(missing_from_catalog):
        findings.append(RbacFinding("catalog-missing-permission", f"Permission `{permission}` is declared in endpoints but missing from catalog."))

    stale_catalog_permissions = catalog_permissions - endpoint_permissions
    for permission in sorted(stale_catalog_permissions):
        findings.append(RbacFinding("catalog-stale-permission", f"Permission `{permission}` exists in catalog but is not declared by endpoints."))

    roles_by_name = {role.get("nombre"): role for role in roles}
    admin_role = roles_by_name.get("ADMIN_EMPRESA")
    if not admin_role:
        findings.append(RbacFinding("missing-admin-role", "Role seed must include ADMIN_EMPRESA."))
    else:
        admin_permissions = set(admin_role.get("permisos", []))
        for permission in sorted(endpoint_permissions - admin_permissions):
            findings.append(RbacFinding("admin-missing-permission", f"ADMIN_EMPRESA is missing endpoint permission `{permission}`."))

    for role in roles:
        role_name = role.get("nombre", "<unknown>")
        permissions = role.get("permisos", [])
        if not isinstance(permissions, list):
            findings.append(RbacFinding("role-permissions-not-list", f"Role `{role_name}` permissions must be a list."))
            continue
        for permission in permissions:
            if permission == "*":
                continue
            if not isinstance(permission, str) or not PERMISSION_PATTERN.match(permission):
                findings.append(RbacFinding("role-invalid-permission-name", f"Role `{role_name}` has invalid permission `{permission}`."))
                continue
            if permission not in endpoint_permissions:
                findings.append(RbacFinding("role-unknown-permission", f"Role `{role_name}` references unknown permission `{permission}`."))

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoints-dir", type=Path, default=ENDPOINTS_DIR)
    parser.add_argument("--catalog", type=Path, default=CATALOG_PATH)
    parser.add_argument("--role-seed", type=Path, default=ROLE_SEED_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = audit_rbac_coverage(endpoints_dir=args.endpoints_dir, catalog_path=args.catalog, role_seed_path=args.role_seed)
    if findings:
        for finding in findings:
            print(f"❌ {finding.code}: {finding.detail}")
        return 1
    print("✅ RBAC coverage audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
