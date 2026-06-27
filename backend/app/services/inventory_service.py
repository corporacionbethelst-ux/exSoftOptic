from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventario import CapaInventario, InventarioExistencia, KardexMovimiento
from app.models.producto import Producto


class InventoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _existencia(self, empresa_id: UUID, sucursal_id: UUID, producto_id: UUID) -> InventarioExistencia:
        result = await self.db.execute(
            select(InventarioExistencia).where(
                InventarioExistencia.empresa_id == empresa_id,
                InventarioExistencia.sucursal_id == sucursal_id,
                InventarioExistencia.producto_id == producto_id,
            ).with_for_update()
        )
        existencia = result.scalar_one_or_none()
        if existencia is None:
            existencia = InventarioExistencia(empresa_id=empresa_id, sucursal_id=sucursal_id, producto_id=producto_id)
            self.db.add(existencia)
            await self.db.flush()
        return existencia

    async def entrada(self, *, empresa_id: UUID, sucursal_id: UUID, producto_id: UUID, cantidad: Decimal, costo_unitario: Decimal, origen: str, referencia: str | None = None, lote: str | None = None, numero_serie: str | None = None, fecha_caducidad: date | None = None) -> KardexMovimiento:
        if cantidad <= 0 or costo_unitario < 0:
            raise ValueError("La entrada requiere cantidad positiva y costo no negativo")
        existencia = await self._existencia(empresa_id, sucursal_id, producto_id)
        producto = await self.db.get(Producto, producto_id)
        if producto is None or producto.empresa_id != empresa_id:
            raise ValueError("Producto inexistente para la empresa")
        capa = CapaInventario(empresa_id=empresa_id, sucursal_id=sucursal_id, producto_id=producto_id, lote=lote, numero_serie=numero_serie, fecha_caducidad=fecha_caducidad, cantidad_inicial=cantidad, cantidad_disponible=cantidad, costo_unitario=costo_unitario, referencia=referencia)
        self.db.add(capa)
        existencia.cantidad += cantidad
        existencia.valor_total += cantidad * costo_unitario
        existencia.costo_promedio = existencia.valor_total / existencia.cantidad if existencia.cantidad else Decimal("0")
        mov = KardexMovimiento(empresa_id=empresa_id, sucursal_id=sucursal_id, producto_id=producto_id, tipo_movimiento="ENTRADA", origen=origen, referencia=referencia, cantidad=cantidad, costo_unitario=costo_unitario, costo_total=cantidad * costo_unitario, saldo_cantidad=existencia.cantidad, saldo_valor=existencia.valor_total, lote=lote, numero_serie=numero_serie)
        self.db.add(mov)
        await self.db.flush()
        return mov

    async def salida_peps(self, *, empresa_id: UUID, sucursal_id: UUID, producto_id: UUID, cantidad: Decimal, origen: str, referencia: str | None = None) -> tuple[KardexMovimiento, Decimal]:
        if cantidad <= 0:
            raise ValueError("La salida requiere cantidad positiva")
        existencia = await self._existencia(empresa_id, sucursal_id, producto_id)
        if existencia.cantidad < cantidad:
            raise ValueError("Inventario insuficiente")
        result = await self.db.execute(
            select(CapaInventario).where(CapaInventario.empresa_id == empresa_id, CapaInventario.sucursal_id == sucursal_id, CapaInventario.producto_id == producto_id, CapaInventario.cantidad_disponible > 0).order_by(CapaInventario.created_at, CapaInventario.id).with_for_update()
        )
        restante = cantidad
        costo_total = Decimal("0")
        for capa in result.scalars().all():
            consumir = min(restante, capa.cantidad_disponible)
            capa.cantidad_disponible -= consumir
            costo_total += consumir * capa.costo_unitario
            restante -= consumir
            if restante == 0:
                break
        if restante > 0:
            raise ValueError("Capas PEPS insuficientes para cubrir la salida")
        existencia.cantidad -= cantidad
        existencia.valor_total -= costo_total
        if existencia.valor_total < 0:
            existencia.valor_total = Decimal("0")
        existencia.costo_promedio = existencia.valor_total / existencia.cantidad if existencia.cantidad else Decimal("0")
        mov = KardexMovimiento(empresa_id=empresa_id, sucursal_id=sucursal_id, producto_id=producto_id, tipo_movimiento="SALIDA", origen=origen, referencia=referencia, cantidad=-cantidad, costo_unitario=costo_total / cantidad, costo_total=-costo_total, saldo_cantidad=existencia.cantidad, saldo_valor=existencia.valor_total)
        self.db.add(mov)
        await self.db.flush()
        return mov, costo_total
