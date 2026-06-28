#!/usr/bin/env python3
"""Generate baseline RBAC role seed JSON from the backend permission catalog."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

CATALOG = Path("../docs/backend-permissions.md")
DEFAULT_OUTPUT = Path("seeds/roles.base.json")

ROLE_MODULES = {
    "VENTAS_CAJA": ["ventas", "facturacion", "crm"],
    "INVENTARIO": ["inventario", "productos", "compras"],
    "TESORERIA": ["tesoreria"],
    "CONTABILIDAD": ["contabilidad", "reportes"],
    "LABORATORIO": ["laboratorio", "garantias"],
    "REPORTES": ["reportes"],
    "SOPORTE_OPERATIVO": ["observabilidad", "auditoria", "outbox"],
}


def parse_catalog(catalog_path: Path = CATALOG) -> dict[str, list[str]]:
    permissions_by_module: dict[str, list[str]] = {}
    current_module: str | None = None
    for line in catalog_path.read_text().splitlines():
        if line.startswith("## "):
            current_module = line.removeprefix("## ").strip()
            permissions_by_module[current_module] = []
        elif current_module and line.startswith("- `") and line.endswith("`"):
            permissions_by_module[current_module].append(line[3:-1])
    return permissions_by_module


def build_roles(permissions_by_module: dict[str, list[str]]) -> list[dict]:
    all_permissions = sorted({permission for permissions in permissions_by_module.values() for permission in permissions})
    roles = [
        {
            "nombre": "SUPER_ADMIN",
            "descripcion": "Acceso total de emergencia y administración global.",
            "es_sistema": True,
            "nivel_acceso": 100,
            "permisos": ["*"],
        },
        {
            "nombre": "ADMIN_EMPRESA",
            "descripcion": "Administrador operativo de empresa con todos los permisos declarados.",
            "es_sistema": True,
            "nivel_acceso": 90,
            "permisos": all_permissions,
        },
    ]
    for role_name, modules in ROLE_MODULES.items():
        role_permissions = sorted(
            {permission for module in modules for permission in permissions_by_module.get(module, [])}
        )
        roles.append(
            {
                "nombre": role_name,
                "descripcion": f"Rol base para módulos: {', '.join(modules)}.",
                "es_sistema": True,
                "nivel_acceso": 50,
                "permisos": role_permissions,
            }
        )
    return roles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate baseline role seed JSON")
    parser.add_argument("--catalog", type=Path, default=CATALOG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    rendered = json.dumps(build_roles(parse_catalog(args.catalog)), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        current = args.output.read_text() if args.output.exists() else ""
        if current != rendered:
            print(f"❌ role seed is out of date: {args.output}")
            return 1
        print("✅ role seed is up to date")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered)
    print(f"✅ role seed written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
