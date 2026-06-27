from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventario import InventarioExistencia
from app.models.producto import Producto
from app.schemas.inventory_accounting import InventarioAlertaResponse


@dataclass(frozen=True)
class InventoryAlertPolicy:
    stock_critico_factor: Decimal = Decimal("0.50")


class InventoryAlertService:
    def __init__(self, db: AsyncSession, policy: InventoryAlertPolicy | None = None):
        self.db = db
        self.policy = policy or InventoryAlertPolicy()

    async def alertas_stock_minimo(self, *, empresa_id: UUID, sucursal_id: UUID | None = None) -> list[InventarioAlertaResponse]:
        query: Select = (
            select(InventarioExistencia, Producto)
            .join(Producto, Producto.id == InventarioExistencia.producto_id)
            .where(
                InventarioExistencia.empresa_id == empresa_id,
                Producto.empresa_id == empresa_id,
                Producto.es_servicio.is_(False),
                Producto.stock_minimo > 0,
                InventarioExistencia.cantidad <= Producto.stock_minimo,
            )
            .order_by(InventarioExistencia.cantidad.asc(), Producto.sku.asc())
        )
        if sucursal_id:
            query = query.where(InventarioExistencia.sucursal_id == sucursal_id)
        rows = (await self.db.execute(query)).all()
        return [self._to_alerta(existencia, producto) for existencia, producto in rows]

    def _to_alerta(self, existencia: InventarioExistencia, producto: Producto) -> InventarioAlertaResponse:
        stock_minimo = Decimal(producto.stock_minimo or 0)
        cantidad = Decimal(existencia.cantidad or 0)
        severidad = "CRITICA" if cantidad <= (stock_minimo * self.policy.stock_critico_factor) else "MEDIA"
        return InventarioAlertaResponse(
            producto_id=producto.id,
            sucursal_id=existencia.sucursal_id,
            sku=producto.sku,
            nombre=producto.nombre,
            tipo_alerta="STOCK_MINIMO",
            severidad=severidad,
            cantidad_actual=cantidad,
            stock_minimo=stock_minimo,
            punto_reorden=Decimal(producto.punto_reorden or 0),
            valor_total=Decimal(existencia.valor_total or 0),
            mensaje=f"{producto.sku} está por debajo del stock mínimo ({cantidad} <= {stock_minimo})",
        )
