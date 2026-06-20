from datetime import date, datetime, time
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import AsientoContable, CuentaContable, LineaAsientoContable
from app.models.inventario import InventarioExistencia
from app.models.producto import Producto
from app.models.venta import Venta
from app.schemas.reportes import (
    BalanzaComprobacionResponse,
    BalanzaCuentaResponse,
    InventarioValuadoItemResponse,
    InventarioValuadoResponse,
    LibroDiarioLineaResponse,
    LibroDiarioResponse,
    LibroMayorResponse,
    MargenVentasItemResponse,
    MargenVentasResponse,
    MayorCuentaResponse,
    MayorMovimientoResponse,
)


class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def libro_diario(self, *, empresa_id: UUID, fecha_inicio: date | None = None, fecha_fin: date | None = None) -> LibroDiarioResponse:
        query = (
            select(AsientoContable, LineaAsientoContable, CuentaContable)
            .join(LineaAsientoContable, LineaAsientoContable.asiento_id == AsientoContable.id)
            .join(CuentaContable, CuentaContable.id == LineaAsientoContable.cuenta_id)
            .where(AsientoContable.empresa_id == empresa_id, CuentaContable.empresa_id == empresa_id)
            .order_by(AsientoContable.fecha.asc(), AsientoContable.created_at.asc(), CuentaContable.codigo.asc())
        )
        if fecha_inicio:
            query = query.where(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)
        rows = (await self.db.execute(query)).all()
        lineas = [
            LibroDiarioLineaResponse(
                asiento_id=asiento.id,
                fecha=asiento.fecha.isoformat(),
                origen=asiento.origen,
                referencia=asiento.referencia,
                cuenta_codigo=cuenta.codigo,
                cuenta_nombre=cuenta.nombre,
                descripcion=linea.descripcion,
                debe=linea.debe,
                haber=linea.haber,
            )
            for asiento, linea, cuenta in rows
        ]
        return LibroDiarioResponse(
            empresa_id=empresa_id,
            total_debe=sum((linea.debe for linea in lineas), Decimal("0")),
            total_haber=sum((linea.haber for linea in lineas), Decimal("0")),
            lineas=lineas,
        )

    async def libro_mayor(self, *, empresa_id: UUID, cuenta_codigo: str | None = None, fecha_inicio: date | None = None, fecha_fin: date | None = None) -> LibroMayorResponse:
        query = (
            select(CuentaContable, AsientoContable, LineaAsientoContable)
            .join(LineaAsientoContable, LineaAsientoContable.cuenta_id == CuentaContable.id)
            .join(AsientoContable, AsientoContable.id == LineaAsientoContable.asiento_id)
            .where(CuentaContable.empresa_id == empresa_id, AsientoContable.empresa_id == empresa_id)
            .order_by(CuentaContable.codigo.asc(), AsientoContable.fecha.asc(), AsientoContable.created_at.asc())
        )
        if cuenta_codigo:
            query = query.where(CuentaContable.codigo == cuenta_codigo)
        if fecha_inicio:
            query = query.where(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)
        rows = (await self.db.execute(query)).all()
        cuentas: dict[UUID, MayorCuentaResponse] = {}
        saldos: dict[UUID, Decimal] = {}
        for cuenta, asiento, linea in rows:
            if cuenta.id not in cuentas:
                cuentas[cuenta.id] = MayorCuentaResponse(
                    cuenta_id=cuenta.id,
                    codigo=cuenta.codigo,
                    nombre=cuenta.nombre,
                    total_debe=Decimal("0"),
                    total_haber=Decimal("0"),
                    saldo_final=Decimal("0"),
                    movimientos=[],
                )
                saldos[cuenta.id] = Decimal("0")
            saldos[cuenta.id] += linea.debe - linea.haber
            cuenta_response = cuentas[cuenta.id]
            cuenta_response.total_debe += linea.debe
            cuenta_response.total_haber += linea.haber
            cuenta_response.saldo_final = saldos[cuenta.id]
            cuenta_response.movimientos.append(
                MayorMovimientoResponse(
                    asiento_id=asiento.id,
                    fecha=asiento.fecha.isoformat(),
                    referencia=asiento.referencia,
                    descripcion=linea.descripcion,
                    debe=linea.debe,
                    haber=linea.haber,
                    saldo=saldos[cuenta.id],
                )
            )
        return LibroMayorResponse(empresa_id=empresa_id, cuentas=list(cuentas.values()))

    async def balanza_comprobacion(self, *, empresa_id: UUID, fecha_inicio: date | None = None, fecha_fin: date | None = None) -> BalanzaComprobacionResponse:
        query = (
            select(
                CuentaContable.id,
                CuentaContable.codigo,
                CuentaContable.nombre,
                CuentaContable.tipo,
                CuentaContable.naturaleza,
                func.coalesce(func.sum(LineaAsientoContable.debe), 0).label("debe"),
                func.coalesce(func.sum(LineaAsientoContable.haber), 0).label("haber"),
            )
            .join(LineaAsientoContable, LineaAsientoContable.cuenta_id == CuentaContable.id)
            .join(AsientoContable, AsientoContable.id == LineaAsientoContable.asiento_id)
            .where(CuentaContable.empresa_id == empresa_id, AsientoContable.empresa_id == empresa_id)
            .group_by(CuentaContable.id, CuentaContable.codigo, CuentaContable.nombre, CuentaContable.tipo, CuentaContable.naturaleza)
            .order_by(CuentaContable.codigo)
        )
        if fecha_inicio:
            query = query.where(AsientoContable.fecha >= fecha_inicio)
        if fecha_fin:
            query = query.where(AsientoContable.fecha <= fecha_fin)
        rows = (await self.db.execute(query)).all()
        cuentas = [
            BalanzaCuentaResponse(
                cuenta_id=row.id,
                codigo=row.codigo,
                nombre=row.nombre,
                tipo=row.tipo,
                naturaleza=row.naturaleza,
                debe=row.debe,
                haber=row.haber,
                saldo=row.debe - row.haber,
            )
            for row in rows
        ]
        return BalanzaComprobacionResponse(
            empresa_id=empresa_id,
            total_debe=sum((cuenta.debe for cuenta in cuentas), Decimal("0")),
            total_haber=sum((cuenta.haber for cuenta in cuentas), Decimal("0")),
            cuentas=cuentas,
        )

    async def inventario_valuado(self, *, empresa_id: UUID, sucursal_id: UUID | None = None) -> InventarioValuadoResponse:
        query = (
            select(InventarioExistencia, Producto)
            .join(Producto, Producto.id == InventarioExistencia.producto_id)
            .where(InventarioExistencia.empresa_id == empresa_id, Producto.empresa_id == empresa_id)
            .order_by(Producto.sku)
        )
        if sucursal_id:
            query = query.where(InventarioExistencia.sucursal_id == sucursal_id)
        rows = (await self.db.execute(query)).all()
        items = [
            InventarioValuadoItemResponse(
                producto_id=existencia.producto_id,
                sucursal_id=existencia.sucursal_id,
                sku=producto.sku,
                producto=producto.nombre,
                cantidad=existencia.cantidad,
                costo_promedio=existencia.costo_promedio,
                valor_total=existencia.valor_total,
            )
            for existencia, producto in rows
        ]
        return InventarioValuadoResponse(
            empresa_id=empresa_id,
            total_valor=sum((item.valor_total for item in items), Decimal("0")),
            items=items,
        )

    async def margen_ventas(self, *, empresa_id: UUID, fecha_inicio: date | None = None, fecha_fin: date | None = None) -> MargenVentasResponse:
        query = select(Venta).where(Venta.empresa_id == empresa_id, Venta.estado == "CONFIRMADA").order_by(Venta.fecha.desc())
        if fecha_inicio:
            query = query.where(Venta.fecha >= datetime.combine(fecha_inicio, time.min))
        if fecha_fin:
            query = query.where(Venta.fecha <= datetime.combine(fecha_fin, time.max))
        ventas = (await self.db.execute(query)).scalars().all()
        items = []
        for venta in ventas:
            margen = venta.total - venta.costo_total
            porcentaje = (margen / venta.total * Decimal("100")) if venta.total else Decimal("0")
            items.append(
                MargenVentasItemResponse(
                    venta_id=venta.id,
                    folio=venta.folio,
                    total=venta.total,
                    costo_total=venta.costo_total,
                    margen=margen,
                    margen_porcentaje=porcentaje,
                )
            )
        total_ventas = sum((item.total for item in items), Decimal("0"))
        total_costo = sum((item.costo_total for item in items), Decimal("0"))
        margen_total = total_ventas - total_costo
        margen_porcentaje = (margen_total / total_ventas * Decimal("100")) if total_ventas else Decimal("0")
        return MargenVentasResponse(
            empresa_id=empresa_id,
            total_ventas=total_ventas,
            total_costo=total_costo,
            margen_total=margen_total,
            margen_porcentaje=margen_porcentaje,
            ventas=items,
        )
