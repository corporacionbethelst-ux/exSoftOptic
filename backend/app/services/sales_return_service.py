from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.producto import Producto
from app.models.venta import DevolucionVenta, DevolucionVentaLinea, Venta, VentaLinea
from app.schemas.ventas import DevolucionVentaCreate
from app.services.accounting_engine import AccountingEngine
from app.services.inventory_service import InventoryService


class SalesReturnService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def registrar_devolucion(self, *, empresa_id: UUID, venta_id: UUID, payload: DevolucionVentaCreate) -> DevolucionVenta:
        async with self.db.begin_nested():
            venta = await self._get_venta_for_update(empresa_id, venta_id)
            if venta.estado not in {"CONFIRMADA", "PARCIALMENTE_DEVUELTA"}:
                raise ValueError("Solo una venta CONFIRMADA puede devolverse")
            lineas_por_id = {linea.id: linea for linea in venta.lineas}
            devolucion = DevolucionVenta(
                empresa_id=empresa_id,
                sucursal_id=venta.sucursal_id,
                venta_id=venta.id,
                folio=payload.folio,
                motivo=payload.motivo,
                estado="CONFIRMADA",
                subtotal=Decimal("0"),
                impuestos=Decimal("0"),
                total=Decimal("0"),
                costo_total=Decimal("0"),
            )
            self.db.add(devolucion)
            await self.db.flush()

            inventory = InventoryService(self.db)
            subtotal = Decimal("0")
            costo_total = Decimal("0")
            for item in payload.lineas:
                linea = lineas_por_id.get(item.venta_linea_id)
                if linea is None:
                    raise ValueError("La línea no pertenece a la venta")
                devuelto_previo = await self._cantidad_devuelta(linea.id)
                if devuelto_previo + item.cantidad > linea.cantidad:
                    raise ValueError("La cantidad devuelta supera lo vendido")
                importe = (linea.importe / linea.cantidad) * item.cantidad
                costo_linea = (linea.costo_total / linea.cantidad) * item.cantidad if linea.costo_total else Decimal("0")
                producto = await self.db.get(Producto, linea.producto_id)
                if producto is None or producto.empresa_id != empresa_id:
                    raise ValueError("Producto inexistente para la empresa")
                if not producto.es_servicio:
                    await inventory.entrada(
                        empresa_id=empresa_id,
                        sucursal_id=venta.sucursal_id,
                        producto_id=linea.producto_id,
                        cantidad=item.cantidad,
                        costo_unitario=costo_linea / item.cantidad if item.cantidad else Decimal("0"),
                        origen="DEVOLUCION_VENTA",
                        referencia=payload.folio,
                    )
                subtotal += importe
                costo_total += costo_linea
                devolucion.lineas.append(
                    DevolucionVentaLinea(
                        venta_linea_id=linea.id,
                        producto_id=linea.producto_id,
                        cantidad=item.cantidad,
                        importe=importe,
                        costo_total=costo_linea,
                    )
                )
            if subtotal <= 0:
                raise ValueError("La devolución debe tener importe positivo")
            impuestos = (venta.impuestos / venta.subtotal) * subtotal if venta.subtotal else Decimal("0")
            total = subtotal + impuestos
            asiento = await AccountingEngine(self.db).handle_devolucion_venta(
                empresa_id=empresa_id,
                fecha=(venta.fecha or datetime.now(timezone.utc)).date(),
                referencia=payload.folio,
                total=total,
                costo=costo_total,
                cuenta_cobro=payload.cuenta_cobro,
                cuenta_ingresos=payload.cuenta_ingresos,
                cuenta_costo_ventas=payload.cuenta_costo_ventas,
                cuenta_inventario=payload.cuenta_inventario,
            )
            devolucion.subtotal = subtotal
            devolucion.impuestos = impuestos
            devolucion.total = total
            devolucion.costo_total = costo_total
            devolucion.asiento_id = asiento.id
            venta.estado = "DEVUELTA" if await self._venta_totalmente_devuelta(venta) else "PARCIALMENTE_DEVUELTA"
            await self.db.flush()
        return await self.obtener_devolucion(empresa_id=empresa_id, devolucion_id=devolucion.id)

    async def obtener_devolucion(self, *, empresa_id: UUID, devolucion_id: UUID) -> DevolucionVenta:
        result = await self.db.execute(
            select(DevolucionVenta)
            .options(selectinload(DevolucionVenta.lineas))
            .where(DevolucionVenta.empresa_id == empresa_id, DevolucionVenta.id == devolucion_id)
        )
        devolucion = result.scalar_one_or_none()
        if devolucion is None:
            raise ValueError("Devolución inexistente")
        return devolucion

    async def _get_venta_for_update(self, empresa_id: UUID, venta_id: UUID) -> Venta:
        result = await self.db.execute(
            select(Venta)
            .options(selectinload(Venta.lineas))
            .where(Venta.empresa_id == empresa_id, Venta.id == venta_id)
            .with_for_update()
        )
        venta = result.scalar_one_or_none()
        if venta is None:
            raise ValueError("Venta inexistente")
        return venta

    async def _cantidad_devuelta(self, venta_linea_id: UUID) -> Decimal:
        result = await self.db.execute(select(func.coalesce(func.sum(DevolucionVentaLinea.cantidad), 0)).where(DevolucionVentaLinea.venta_linea_id == venta_linea_id))
        return Decimal(result.scalar_one())

    async def _venta_totalmente_devuelta(self, venta: Venta) -> bool:
        for linea in venta.lineas:
            if await self._cantidad_devuelta(linea.id) < linea.cantidad:
                return False
        return True
