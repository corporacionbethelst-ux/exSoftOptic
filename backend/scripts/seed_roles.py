#!/usr/bin/env python3
"""Import baseline RBAC roles from the generated role seed JSON."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

DEFAULT_SEED_PATH = Path("seeds/roles.base.json")


@dataclass(frozen=True)
class RoleSeed:
    nombre: str
    descripcion: str
    es_sistema: bool
    nivel_acceso: int
    permisos: list[str]


def load_role_seed(path: Path = DEFAULT_SEED_PATH) -> list[RoleSeed]:
    raw_roles = json.loads(path.read_text())
    return [
        RoleSeed(
            nombre=role["nombre"],
            descripcion=role.get("descripcion") or "",
            es_sistema=bool(role.get("es_sistema", True)),
            nivel_acceso=int(role.get("nivel_acceso", 1)),
            permisos=sorted(role.get("permisos", [])),
        )
        for role in raw_roles
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--empresa-id", required=True, type=UUID, help="Company UUID that owns the imported roles.")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED_PATH, help="Path to roles.base.json.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing to the database.")
    return parser.parse_args()


async def import_roles(*, empresa_id: UUID, seed_path: Path, dry_run: bool = False) -> dict[str, int | str]:
    from sqlalchemy import select

    from app.core.database import async_session_maker
    from app.models.usuario import Rol

    roles = load_role_seed(seed_path)
    created = 0
    updated = 0
    unchanged = 0
    async with async_session_maker() as session:
        for role in roles:
            result = await session.execute(select(Rol).where(Rol.nombre == role.nombre))
            db_role = result.scalar_one_or_none()
            desired = {
                "descripcion": role.descripcion,
                "es_sistema": role.es_sistema,
                "nivel_acceso": role.nivel_acceso,
                "permisos": role.permisos,
                "empresa_id": empresa_id,
            }
            if db_role is None:
                created += 1
                if not dry_run:
                    session.add(Rol(nombre=role.nombre, **desired))
                continue

            changed = any(getattr(db_role, field) != value for field, value in desired.items())
            if changed:
                updated += 1
                if not dry_run:
                    for field, value in desired.items():
                        setattr(db_role, field, value)
            else:
                unchanged += 1
        if dry_run:
            await session.rollback()
        else:
            await session.commit()
    return {"empresa_id": str(empresa_id), "created": created, "updated": updated, "unchanged": unchanged}


def main() -> int:
    args = parse_args()
    result = asyncio.run(import_roles(empresa_id=args.empresa_id, seed_path=args.seed, dry_run=args.dry_run))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
