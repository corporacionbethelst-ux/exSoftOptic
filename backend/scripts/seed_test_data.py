#!/usr/bin/env python3
"""Seed a minimal deterministic dataset for backend smoke testing."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid5, NAMESPACE_URL

TEST_NAMESPACE = "https://exsoftoptic.local/backend-test-seed"


@dataclass(frozen=True)
class TestSeed:
    empresa_id: UUID
    sucursal_id: UUID
    categoria_id: UUID
    marca_id: UUID
    producto_id: UUID
    rol_id: UUID
    usuario_id: UUID
    rfc: str = "XAXX010101000"
    sucursal_codigo: str = "TEST"
    producto_sku: str = "TEST-ARMAZON-001"
    rol_nombre: str = "TEST_ADMIN"
    username: str = "test.admin"
    email: str = "test.admin@example.com"


def build_seed() -> TestSeed:
    return TestSeed(
        empresa_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/empresa"),
        sucursal_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/sucursal"),
        categoria_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/categoria"),
        marca_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/marca"),
        producto_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/producto"),
        rol_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/rol"),
        usuario_id=uuid5(NAMESPACE_URL, f"{TEST_NAMESPACE}/usuario"),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without writing to the database.")
    parser.add_argument(
        "--admin-password-hash",
        default="not-for-production-test-hash",
        help="Precomputed password hash for the seeded test admin user.",
    )
    return parser.parse_args()


def _normalize(value: object) -> object:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    return value


async def _upsert(session, model, lookup, values, counters) -> object:
    from sqlalchemy import select

    result = await session.execute(select(model).where(*[getattr(model, field) == value for field, value in lookup.items()]))
    instance = result.scalar_one_or_none()
    if instance is None:
        counters["created"] += 1
        instance = model(**lookup, **values)
        session.add(instance)
        return instance

    changed = False
    update_values = {field: value for field, value in values.items() if field != "id"}
    for field, value in update_values.items():
        if _normalize(getattr(instance, field)) != _normalize(value):
            setattr(instance, field, value)
            changed = True
    if changed:
        counters["updated"] += 1
    else:
        counters["unchanged"] += 1
    return instance


async def seed_test_data(*, dry_run: bool = False, admin_password_hash: str = "not-for-production-test-hash") -> dict[str, int | str]:
    from app.core.database import async_session_maker
    from app.models.empresa import Empresa
    from app.models.producto import Categoria, Marca, Producto
    from app.models.sucursal import Sucursal
    from app.models.usuario import Rol, Usuario

    seed = build_seed()
    counters = {"created": 0, "updated": 0, "unchanged": 0}

    async with async_session_maker() as session:
        empresa = await _upsert(
            session,
            Empresa,
            {"rfc": seed.rfc},
            {
                "id": seed.empresa_id,
                "razon_social": "ExSoftOptic Test SA de CV",
                "nombre_comercial": "ExSoftOptic Test",
                "regimen_fiscal": "601",
                "codigo_postal": "06600",
                "moneda_base": "MXN",
                "configuracion_contable": {"testing": True},
            },
            counters,
        )
        await session.flush()
        empresa_id = empresa.id

        sucursal = await _upsert(
            session,
            Sucursal,
            {"empresa_id": empresa_id, "codigo": seed.sucursal_codigo},
            {
                "id": seed.sucursal_id,
                "nombre": "Sucursal Test",
                "direccion": "Av. QA 100",
                "telefono": "+52 55 0000 0000",
                "email": "qa@example.com",
                "codigo_postal": "06600",
                "ciudad": "Ciudad de México",
                "estado": "CDMX",
                "pais": "México",
                "es_principal": True,
            },
            counters,
        )

        categoria = await _upsert(
            session,
            Categoria,
            {"empresa_id": empresa_id, "nombre": "Armazones Test"},
            {"id": seed.categoria_id, "descripcion": "Categoría base para pruebas backend", "icono": "glasses"},
            counters,
        )
        marca = await _upsert(
            session,
            Marca,
            {"empresa_id": empresa_id, "nombre": "Marca Test"},
            {"id": seed.marca_id, "descripcion": "Marca base para pruebas backend"},
            counters,
        )
        await session.flush()

        producto = await _upsert(
            session,
            Producto,
            {"empresa_id": empresa_id, "sku": seed.producto_sku},
            {
                "id": seed.producto_id,
                "categoria_id": categoria.id,
                "marca_id": marca.id,
                "codigo_barras": "7500000000017",
                "nombre": "Armazón Test",
                "descripcion": "Producto base para pruebas backend",
                "tipo_producto": "ARMAZON",
                "unidad_medida": "PIEZA",
                "atributos_opticos": {"material": "acetato", "color": "negro"},
                "costo_estandar": Decimal("500.0000"),
                "precio_venta": Decimal("1200.0000"),
                "precio_mayoreo": Decimal("950.0000"),
                "metodo_costeo": "PEPS",
                "stock_minimo": Decimal("2.000"),
                "stock_maximo": Decimal("20.000"),
                "punto_reorden": Decimal("5.000"),
            },
            counters,
        )

        rol = await _upsert(
            session,
            Rol,
            {"nombre": seed.rol_nombre},
            {
                "id": seed.rol_id,
                "descripcion": "Rol administrativo para pruebas backend",
                "es_sistema": True,
                "permisos": ["*"],
                "nivel_acceso": 100,
                "empresa_id": empresa_id,
            },
            counters,
        )
        await session.flush()

        usuario = await _upsert(
            session,
            Usuario,
            {"username": seed.username},
            {
                "id": seed.usuario_id,
                "empresa_id": empresa_id,
                "email": seed.email,
                "password_hash": admin_password_hash,
                "nombre_completo": "Administrador Test",
                "rol_id": rol.id,
                "sucursal_id": sucursal.id,
                "esta_activo": True,
                "email_verificado": True,
            },
            counters,
        )

        summary = {
            "empresa_id": str(empresa_id),
            "sucursal_id": str(sucursal.id),
            "producto_id": str(producto.id),
            "usuario_id": str(usuario.id),
            **counters,
        }

        if dry_run:
            await session.rollback()
        else:
            await session.commit()

    return summary


def main() -> int:
    args = parse_args()
    result = asyncio.run(seed_test_data(dry_run=args.dry_run, admin_password_hash=args.admin_password_hash))
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
