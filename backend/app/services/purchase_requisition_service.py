from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.models.compra import SolicitudCompra, SolicitudCompraLinea
from app.models.producto import Producto
from app.schemas.compras import SolicitudCompraGenerarRequest
from app.services.inventory_alert_service import InventoryAlertService


class PurchaseRequisitionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generar_desde_stock_minimo(self, *, empresa_id: UUID, payload: SolicitudCompraGenerarRequest) -> SolicitudCompra:
        alertas = await InventoryAlertService(self.db).alertas_stock_minimo(empresa_id=empresa_id, sucursal_id=payload.sucursal_id)
        if not alertas:
            raise ValueError("No hay alertas de stock mínimo para generar solicitud")
        solicitud = SolicitudCompra(
            empresa_id=empresa_id,
            sucursal_id=payload.sucursal_id,
            folio=payload.folio,
            origen="STOCK_MINIMO",
            estado="BORRADOR",
            observaciones=payload.observaciones,
        )
        self.db.add(solicitud)
        await self.db.flush()
        for alerta in alertas:
            producto = await self.db.get(Producto, alerta.producto_id)
            objetivo = Decimal(producto.punto_reorden or 0) if producto and producto.punto_reorden else alerta.stock_minimo
            cantidad_sugerida = max(objetivo - alerta.cantidad_actual, Decimal("0"))
            if cantidad_sugerida <= 0:
                cantidad_sugerida = alerta.stock_minimo - alerta.cantidad_actual
            solicitud.lineas.append(
                SolicitudCompraLinea(
                    producto_id=alerta.producto_id,
                    cantidad_sugerida=cantidad_sugerida,
                    costo_estimado=Decimal(producto.costo_estandar or 0) if producto else Decimal("0"),
                    motivo=alerta.mensaje,
                )
            )
        await self.db.flush()
        return await self.obtener_solicitud(empresa_id=empresa_id, solicitud_id=solicitud.id)

    async def obtener_solicitud(self, *, empresa_id: UUID, solicitud_id: UUID) -> SolicitudCompra:
        result = await self.db.execute(
            select(SolicitudCompra)
            .options(selectinload(SolicitudCompra.lineas))
            .where(SolicitudCompra.empresa_id == empresa_id, SolicitudCompra.id == solicitud_id)
        )
        solicitud = result.scalar_one_or_none()
        if solicitud is None:
            raise ValueError("Solicitud de compra inexistente")
        return solicitud
