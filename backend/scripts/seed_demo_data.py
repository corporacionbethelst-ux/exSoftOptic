#!/usr/bin/env python3
"""Seed an idempotent demo dataset for frontend development.

Run after the base seed (`make seed`). The dataset is intentionally small but
covers the main screens: catalogs, inventory, CRM, sales, invoices, purchases
and lab orders.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

from sqlalchemy import delete, select

DEMO_NAMESPACE = "https://exsoftoptic.local/demo-seed/v1"
DEMO_EMPRESA_RFC = "ODE260618ABC"
DEMO_SUCURSAL_CODIGO = "MAIN"


def demo_id(name: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"{DEMO_NAMESPACE}/{name}")


@dataclass(frozen=True)
class DemoContext:
    empresa_id: UUID
    sucursal_id: UUID
    admin_user_id: UUID | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview the seed without committing changes.")
    parser.add_argument(
        "--reset-demo",
        action="store_true",
        help="Delete and recreate deterministic demo detail rows before seeding.",
    )
    return parser.parse_args()


def normalize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


async def upsert(session, model, lookup: dict[str, Any], values: dict[str, Any], counters: dict[str, int]):
    result = await session.execute(
        select(model).where(*[getattr(model, field) == value for field, value in lookup.items()])
    )
    instance = result.scalar_one_or_none()
    if instance is None:
        instance = model(**lookup, **values)
        session.add(instance)
        counters["created"] += 1
        return instance

    changed = False
    for field, value in values.items():
        if field in lookup:
            continue
        if normalize(getattr(instance, field)) != normalize(value):
            setattr(instance, field, value)
            changed = True
    counters["updated" if changed else "unchanged"] += 1
    return instance


async def delete_demo_rows(session, model, ids: Iterable[UUID]) -> None:
    ids = list(ids)
    if ids:
        await session.execute(delete(model).where(model.id.in_(ids)))


async def load_context(session) -> DemoContext:
    from app.models.empresa import Empresa
    from app.models.sucursal import Sucursal
    from app.models.usuario import Usuario

    empresa = (
        await session.execute(select(Empresa).where(Empresa.rfc == DEMO_EMPRESA_RFC))
    ).scalar_one_or_none()
    if empresa is None:
        raise RuntimeError("No existe la empresa demo. Ejecuta primero: make seed")

    sucursal = (
        await session.execute(
            select(Sucursal).where(Sucursal.empresa_id == empresa.id, Sucursal.codigo == DEMO_SUCURSAL_CODIGO)
        )
    ).scalar_one_or_none()
    if sucursal is None:
        raise RuntimeError("No existe la sucursal MAIN. Ejecuta primero: make seed")

    admin = (await session.execute(select(Usuario).where(Usuario.username == "admin"))).scalar_one_or_none()
    return DemoContext(empresa_id=empresa.id, sucursal_id=sucursal.id, admin_user_id=admin.id if admin else None)


async def seed_demo_data(*, dry_run: bool = False, reset_demo: bool = False) -> dict[str, Any]:
    from app.core.database import async_session_maker
    from app.models.compra import Proveedor, OrdenCompra, OrdenCompraLinea, RecepcionCompra, RecepcionCompraLinea
    from app.models.crm import CitaOptica, RecordatorioCliente
    from app.models.factura import Factura, FacturaEvento, FacturaLinea
    from app.models.inventario import CapaInventario, InventarioExistencia, KardexMovimiento
    from app.models.laboratorio import ControlCalidadLaboratorio, OrdenLaboratorio, OrdenLaboratorioEtapa
    from app.models.producto import Categoria, Marca, Producto
    from app.models.venta import Cliente, Paciente, PagoVenta, RecetaOptica, Venta, VentaLinea

    counters = {"created": 0, "updated": 0, "unchanged": 0}
    now = datetime.now(timezone.utc)

    async with async_session_maker() as session:
        ctx = await load_context(session)

        if reset_demo:
            await delete_demo_rows(session, FacturaEvento, [demo_id("factura-evento-timbrada")])
            await delete_demo_rows(session, FacturaLinea, [demo_id("factura-linea-1"), demo_id("factura-linea-2")])
            await delete_demo_rows(session, Factura, [demo_id("factura-1")])
            await delete_demo_rows(session, OrdenLaboratorioEtapa, [demo_id(f"lab-etapa-{name}") for name in ["recepcion", "biselado", "calidad"]])
            await delete_demo_rows(session, ControlCalidadLaboratorio, [demo_id("lab-control-1")])
            await delete_demo_rows(session, OrdenLaboratorio, [demo_id("lab-orden-1")])
            await delete_demo_rows(session, PagoVenta, [demo_id("venta-pago-1")])
            await delete_demo_rows(session, VentaLinea, [demo_id("venta-linea-1"), demo_id("venta-linea-2")])
            await delete_demo_rows(session, Venta, [demo_id("venta-1")])
            await delete_demo_rows(session, RecepcionCompraLinea, [demo_id("recepcion-linea-1"), demo_id("recepcion-linea-2")])
            await delete_demo_rows(session, RecepcionCompra, [demo_id("recepcion-1")])
            await delete_demo_rows(session, OrdenCompraLinea, [demo_id("oc-linea-1"), demo_id("oc-linea-2")])
            await delete_demo_rows(session, OrdenCompra, [demo_id("oc-1")])
            await delete_demo_rows(session, RecordatorioCliente, [demo_id("recordatorio-1")])
            await delete_demo_rows(session, CitaOptica, [demo_id("cita-1")])
            await session.flush()

        categoria_armazones = await upsert(
            session,
            Categoria,
            {"empresa_id": ctx.empresa_id, "nombre": "Armazones Demo"},
            {"id": demo_id("categoria-armazones"), "descripcion": "Armazones para venta de mostrador", "icono": "glasses", "esta_activa": True},
            counters,
        )
        categoria_lentes = await upsert(
            session,
            Categoria,
            {"empresa_id": ctx.empresa_id, "nombre": "Lentes Oftálmicos Demo"},
            {"id": demo_id("categoria-lentes"), "descripcion": "Micas y tratamientos", "icono": "lens", "esta_activa": True},
            counters,
        )
        categoria_servicios = await upsert(
            session,
            Categoria,
            {"empresa_id": ctx.empresa_id, "nombre": "Servicios Demo"},
            {"id": demo_id("categoria-servicios"), "descripcion": "Servicios profesionales", "icono": "service", "esta_activa": True},
            counters,
        )

        marca_vista = await upsert(session, Marca, {"empresa_id": ctx.empresa_id, "nombre": "VistaPlus Demo"}, {"id": demo_id("marca-vistaplus"), "descripcion": "Marca demo de armazones", "esta_activa": True}, counters)
        marca_clara = await upsert(session, Marca, {"empresa_id": ctx.empresa_id, "nombre": "ClaraLens Demo"}, {"id": demo_id("marca-claralens"), "descripcion": "Marca demo de lentes", "esta_activa": True}, counters)
        await session.flush()

        products_payload = [
            ("armazon-acetato", categoria_armazones.id, marca_vista.id, "DEMO-ARM-001", "7501000000010", "Armazón Acetato Negro Demo", "ARMAZON", Decimal("420.0000"), Decimal("1299.0000"), False, {"material": "acetato", "color": "negro"}),
            ("armazon-metal", categoria_armazones.id, marca_vista.id, "DEMO-ARM-002", "7501000000027", "Armazón Metal Dorado Demo", "ARMAZON", Decimal("510.0000"), Decimal("1499.0000"), False, {"material": "metal", "color": "dorado"}),
            ("mica-mono", categoria_lentes.id, marca_clara.id, "DEMO-LEN-001", "7501000000034", "Mica Monofocal CR-39 Demo", "LENTE", Decimal("160.0000"), Decimal("650.0000"), True, {"indice": "1.56", "tipo": "monofocal"}),
            ("mica-prog", categoria_lentes.id, marca_clara.id, "DEMO-LEN-002", "7501000000041", "Mica Progresiva Antirreflejante Demo", "LENTE", Decimal("550.0000"), Decimal("2400.0000"), True, {"indice": "1.60", "tipo": "progresivo", "tratamiento": "AR"}),
            ("examen-visual", categoria_servicios.id, None, "DEMO-SRV-001", "7501000000058", "Examen Visual Demo", "SERVICIO", Decimal("0.0000"), Decimal("350.0000"), False, {"duracion_minutos": 30}),
        ]
        productos = {}
        for name, categoria_id, marca_id, sku, barcode, nombre, tipo, costo, precio, requiere_receta, attrs in products_payload:
            productos[name] = await upsert(
                session,
                Producto,
                {"empresa_id": ctx.empresa_id, "sku": sku},
                {
                    "id": demo_id(f"producto-{name}"),
                    "categoria_id": categoria_id,
                    "marca_id": marca_id,
                    "codigo_barras": barcode,
                    "nombre": nombre,
                    "descripcion": f"Producto demo para frontend: {nombre}",
                    "tipo_producto": tipo,
                    "unidad_medida": "SERVICIO" if tipo == "SERVICIO" else "PIEZA",
                    "atributos_opticos": attrs,
                    "costo_estandar": costo,
                    "precio_venta": precio,
                    "precio_mayoreo": precio * Decimal("0.85"),
                    "metodo_costeo": "PEPS",
                    "stock_minimo": Decimal("2.000"),
                    "stock_maximo": Decimal("30.000"),
                    "punto_reorden": Decimal("5.000"),
                    "requiere_receta": requiere_receta,
                    "requiere_lote": tipo != "SERVICIO",
                    "requiere_serie": False,
                    "es_servicio": tipo == "SERVICIO",
                },
                counters,
            )
        await session.flush()

        proveedor = await upsert(session, Proveedor, {"empresa_id": ctx.empresa_id, "rfc": "DOPD010101AB1"}, {"id": demo_id("proveedor-1"), "nombre": "Distribuidora Óptica Demo", "email": "compras@proveedor-demo.com", "telefono": "+52 55 1111 2222"}, counters)
        cliente_ana = await upsert(session, Cliente, {"empresa_id": ctx.empresa_id, "email": "ana.garcia.demo@example.com"}, {"id": demo_id("cliente-ana"), "nombre": "Ana García Demo", "telefono": "+52 55 2222 1001", "rfc": "XAXX010101000", "codigo_postal": "06600", "regimen_fiscal": "616"}, counters)
        cliente_carlos = await upsert(session, Cliente, {"empresa_id": ctx.empresa_id, "email": "carlos.lopez.demo@example.com"}, {"id": demo_id("cliente-carlos"), "nombre": "Carlos López Demo", "telefono": "+52 55 2222 1002", "rfc": "XAXX010101000", "codigo_postal": "44100", "regimen_fiscal": "616"}, counters)
        await session.flush()

        paciente_ana = await upsert(session, Paciente, {"id": demo_id("paciente-ana")}, {"empresa_id": ctx.empresa_id, "cliente_id": cliente_ana.id, "nombre": "Ana García Demo", "fecha_nacimiento": date(1990, 5, 14), "telefono": cliente_ana.telefono, "email": cliente_ana.email}, counters)
        paciente_carlos = await upsert(session, Paciente, {"id": demo_id("paciente-carlos")}, {"empresa_id": ctx.empresa_id, "cliente_id": cliente_carlos.id, "nombre": "Carlos López Demo", "fecha_nacimiento": date(1984, 10, 2), "telefono": cliente_carlos.telefono, "email": cliente_carlos.email}, counters)
        receta_ana = await upsert(session, RecetaOptica, {"id": demo_id("receta-ana")}, {"empresa_id": ctx.empresa_id, "paciente_id": paciente_ana.id, "fecha": date.today(), "od_esfera": Decimal("-1.25"), "od_cilindro": Decimal("-0.50"), "od_eje": Decimal("90"), "oi_esfera": Decimal("-1.00"), "oi_cilindro": Decimal("-0.25"), "oi_eje": Decimal("85"), "dnp": Decimal("62.00"), "altura": Decimal("18.00"), "observaciones": "Receta demo para venta y laboratorio"}, counters)
        await session.flush()

        cita = await upsert(session, CitaOptica, {"empresa_id": ctx.empresa_id, "folio": "CITA-DEMO-001"}, {"id": demo_id("cita-1"), "sucursal_id": ctx.sucursal_id, "cliente_id": cliente_ana.id, "paciente_id": paciente_ana.id, "optometrista_id": ctx.admin_user_id, "fecha_inicio": now + timedelta(days=1, hours=2), "fecha_fin": now + timedelta(days=1, hours=2, minutes=30), "tipo": "EXAMEN_VISUAL", "estado": "PROGRAMADA", "motivo": "Revisión anual demo", "observaciones": "Cita creada por seed demo"}, counters)
        await upsert(session, RecordatorioCliente, {"id": demo_id("recordatorio-1")}, {"empresa_id": ctx.empresa_id, "cliente_id": cliente_ana.id, "paciente_id": paciente_ana.id, "cita_id": cita.id, "tipo": "CITA", "canal": "EMAIL", "programado_para": now + timedelta(hours=12), "estado": "PENDIENTE", "mensaje": "Recordatorio demo de cita óptica"}, counters)

        oc = await upsert(session, OrdenCompra, {"empresa_id": ctx.empresa_id, "folio": "OC-DEMO-001"}, {"id": demo_id("oc-1"), "sucursal_id": ctx.sucursal_id, "proveedor_id": proveedor.id, "estado": "RECIBIDA", "subtotal": Decimal("3700.0000"), "impuestos": Decimal("592.0000"), "total": Decimal("4292.0000")}, counters)
        await session.flush()
        oc_linea_1 = await upsert(session, OrdenCompraLinea, {"id": demo_id("oc-linea-1")}, {"orden_id": oc.id, "producto_id": productos["armazon-acetato"].id, "descripcion": productos["armazon-acetato"].nombre, "cantidad": Decimal("5.000"), "cantidad_recibida": Decimal("5.000"), "costo_unitario": Decimal("420.0000"), "importe": Decimal("2100.0000")}, counters)
        oc_linea_2 = await upsert(session, OrdenCompraLinea, {"id": demo_id("oc-linea-2")}, {"orden_id": oc.id, "producto_id": productos["mica-mono"].id, "descripcion": productos["mica-mono"].nombre, "cantidad": Decimal("10.000"), "cantidad_recibida": Decimal("10.000"), "costo_unitario": Decimal("160.0000"), "importe": Decimal("1600.0000")}, counters)
        recepcion = await upsert(session, RecepcionCompra, {"empresa_id": ctx.empresa_id, "folio": "REC-DEMO-001"}, {"id": demo_id("recepcion-1"), "sucursal_id": ctx.sucursal_id, "orden_id": oc.id, "estado": "RECIBIDA", "total": Decimal("3700.0000")}, counters)
        await session.flush()
        await upsert(session, RecepcionCompraLinea, {"id": demo_id("recepcion-linea-1")}, {"recepcion_id": recepcion.id, "orden_linea_id": oc_linea_1.id, "producto_id": productos["armazon-acetato"].id, "cantidad": Decimal("5.000"), "costo_unitario": Decimal("420.0000"), "importe": Decimal("2100.0000"), "lote": "DEMO-ARM-2026"}, counters)
        await upsert(session, RecepcionCompraLinea, {"id": demo_id("recepcion-linea-2")}, {"recepcion_id": recepcion.id, "orden_linea_id": oc_linea_2.id, "producto_id": productos["mica-mono"].id, "cantidad": Decimal("10.000"), "costo_unitario": Decimal("160.0000"), "importe": Decimal("1600.0000"), "lote": "DEMO-LEN-2026"}, counters)

        inventory_rows = [("armazon-acetato", Decimal("4.000"), Decimal("1680.0000"), Decimal("420.0000")), ("armazon-metal", Decimal("3.000"), Decimal("1530.0000"), Decimal("510.0000")), ("mica-mono", Decimal("8.000"), Decimal("1280.0000"), Decimal("160.0000")), ("mica-prog", Decimal("4.000"), Decimal("2200.0000"), Decimal("550.0000"))]
        for product_key, qty, value, avg_cost in inventory_rows:
            producto = productos[product_key]
            await upsert(session, InventarioExistencia, {"empresa_id": ctx.empresa_id, "sucursal_id": ctx.sucursal_id, "producto_id": producto.id}, {"id": demo_id(f"existencia-{product_key}"), "cantidad": qty, "valor_total": value, "costo_promedio": avg_cost}, counters)
            await upsert(session, CapaInventario, {"id": demo_id(f"capa-{product_key}")}, {"empresa_id": ctx.empresa_id, "sucursal_id": ctx.sucursal_id, "producto_id": producto.id, "lote": f"LOTE-{product_key.upper()}", "cantidad_inicial": qty, "cantidad_disponible": qty, "costo_unitario": avg_cost, "referencia": "SEED-DEMO", "created_at": now - timedelta(days=3)}, counters)
            await upsert(session, KardexMovimiento, {"id": demo_id(f"kardex-{product_key}")}, {"empresa_id": ctx.empresa_id, "sucursal_id": ctx.sucursal_id, "producto_id": producto.id, "tipo_movimiento": "ENTRADA", "origen": "SEED_DEMO", "referencia": "SEED-DEMO", "cantidad": qty, "costo_unitario": avg_cost, "costo_total": value, "saldo_cantidad": qty, "saldo_valor": value, "lote": f"LOTE-{product_key.upper()}"}, counters)

        venta = await upsert(session, Venta, {"empresa_id": ctx.empresa_id, "folio": "VTA-DEMO-001"}, {"id": demo_id("venta-1"), "sucursal_id": ctx.sucursal_id, "cliente_id": cliente_ana.id, "paciente_id": paciente_ana.id, "receta_id": receta_ana.id, "estado": "CONFIRMADA", "subtotal": Decimal("1949.0000"), "impuestos": Decimal("311.8400"), "total": Decimal("2260.8400"), "costo_total": Decimal("580.0000")}, counters)
        await session.flush()
        venta_linea_1 = await upsert(session, VentaLinea, {"id": demo_id("venta-linea-1")}, {"venta_id": venta.id, "producto_id": productos["armazon-acetato"].id, "descripcion": productos["armazon-acetato"].nombre, "cantidad": Decimal("1.000"), "precio_unitario": Decimal("1299.0000"), "descuento": Decimal("0.0000"), "importe": Decimal("1299.0000"), "costo_total": Decimal("420.0000")}, counters)
        venta_linea_2 = await upsert(session, VentaLinea, {"id": demo_id("venta-linea-2")}, {"venta_id": venta.id, "producto_id": productos["mica-mono"].id, "descripcion": productos["mica-mono"].nombre, "cantidad": Decimal("1.000"), "precio_unitario": Decimal("650.0000"), "descuento": Decimal("0.0000"), "importe": Decimal("650.0000"), "costo_total": Decimal("160.0000")}, counters)
        await upsert(session, PagoVenta, {"id": demo_id("venta-pago-1")}, {"venta_id": venta.id, "metodo_pago": "TARJETA", "monto": Decimal("2260.8400"), "referencia": "AUT-DEMO-001"}, counters)

        factura = await upsert(session, Factura, {"empresa_id": ctx.empresa_id, "folio": "FAC-DEMO-001"}, {"id": demo_id("factura-1"), "sucursal_id": ctx.sucursal_id, "venta_id": venta.id, "cliente_id": cliente_ana.id, "estado": "TIMBRADA", "moneda": "MXN", "subtotal": Decimal("1949.0000"), "impuestos": Decimal("311.8400"), "total": Decimal("2260.8400"), "proveedor": "MOCK", "uuid_fiscal": "DEMO-FISCAL-UUID-0001", "xml_url": "https://example.com/demo/fac-demo-001.xml", "pdf_url": "https://example.com/demo/fac-demo-001.pdf", "fecha_timbrado": now}, counters)
        await session.flush()
        await upsert(session, FacturaLinea, {"id": demo_id("factura-linea-1")}, {"factura_id": factura.id, "producto_id": productos["armazon-acetato"].id, "descripcion": venta_linea_1.descripcion, "cantidad": venta_linea_1.cantidad, "precio_unitario": venta_linea_1.precio_unitario, "descuento": Decimal("0.0000"), "importe": venta_linea_1.importe}, counters)
        await upsert(session, FacturaLinea, {"id": demo_id("factura-linea-2")}, {"factura_id": factura.id, "producto_id": productos["mica-mono"].id, "descripcion": venta_linea_2.descripcion, "cantidad": venta_linea_2.cantidad, "precio_unitario": venta_linea_2.precio_unitario, "descuento": Decimal("0.0000"), "importe": venta_linea_2.importe}, counters)
        await upsert(session, FacturaEvento, {"id": demo_id("factura-evento-timbrada")}, {"factura_id": factura.id, "tipo_evento": "TIMBRADA", "descripcion": "Factura demo timbrada con proveedor MOCK"}, counters)

        lab = await upsert(session, OrdenLaboratorio, {"empresa_id": ctx.empresa_id, "folio": "LAB-DEMO-001"}, {"id": demo_id("lab-orden-1"), "sucursal_id": ctx.sucursal_id, "venta_id": venta.id, "paciente_id": paciente_ana.id, "receta_id": receta_ana.id, "estado": "EN_PROCESO", "prioridad": "NORMAL", "fecha_prometida": now + timedelta(days=3), "fecha_inicio": now - timedelta(hours=2), "observaciones": "Orden demo para tablero de laboratorio"}, counters)
        await session.flush()
        for idx, (name, etapa, estado) in enumerate([("recepcion", "RECEPCION", "COMPLETADA"), ("biselado", "BISELADO", "EN_PROCESO"), ("calidad", "CONTROL_CALIDAD", "PENDIENTE")]):
            await upsert(session, OrdenLaboratorioEtapa, {"orden_id": lab.id, "etapa": etapa}, {"id": demo_id(f"lab-etapa-{name}"), "estado": estado, "responsable_id": ctx.admin_user_id, "fecha_inicio": now - timedelta(hours=2 - idx), "fecha_fin": now - timedelta(hours=1) if estado == "COMPLETADA" else None, "observaciones": f"Etapa demo {etapa}"}, counters)
        await upsert(session, ControlCalidadLaboratorio, {"id": demo_id("lab-control-1")}, {"orden_id": lab.id, "resultado": "PENDIENTE", "observaciones": "Control demo pendiente", "usuario_id": ctx.admin_user_id, "fecha": now}, counters)

        summary = {"empresa_id": str(ctx.empresa_id), "sucursal_id": str(ctx.sucursal_id), "productos": len(productos), "clientes": 2, "ventas": 1, "compras": 1, "facturas": 1, "ordenes_laboratorio": 1, **counters}
        if dry_run:
            await session.rollback()
            summary["dry_run"] = True
        else:
            await session.commit()
            summary["dry_run"] = False
        return summary


def main() -> int:
    args = parse_args()
    result = asyncio.run(seed_demo_data(dry_run=args.dry_run, reset_demo=args.reset_demo))
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
