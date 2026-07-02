from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.compra import OrdenCompra, OrdenCompraLinea, Proveedor, RecepcionCompra, RecepcionCompraLinea
from app.models.producto import Producto
from app.schemas.compras import OrdenCompraCreate, RecepcionCompraCreate
from app.schemas.outbox import OutboxEventCreate
from app.services.accounting_engine import AccountingEngine
from app.services.inventory_service import InventoryService
from app.services.outbox_service import OutboxService


class PurchaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_orden(self, *, empresa_id: UUID, payload: OrdenCompraCreate) -> OrdenCompra:
        proveedor = await self._resolver_proveedor(empresa_id, payload)
        subtotal = sum((linea.importe for linea in payload.lineas), Decimal("0"))
        orden = OrdenCompra(
            empresa_id=empresa_id,
            sucursal_id=payload.sucursal_id,
            proveedor_id=proveedor.id,
            folio=payload.folio,
            estado="BORRADOR",
            subtotal=subtotal,
            impuestos=payload.impuestos,
            total=subtotal + payload.impuestos,
        )
        self.db.add(orden)
        await self.db.flush()
        for linea in payload.lineas:
            producto = await self._get_producto(empresa_id, linea.producto_id)
            orden.lineas.append(
                OrdenCompraLinea(
                    producto_id=producto.id,
                    descripcion=linea.descripcion or producto.nombre,
                    cantidad=linea.cantidad,
                    cantidad_recibida=Decimal("0"),
                    costo_unitario=linea.costo_unitario,
                    importe=linea.importe,
                )
            )
        await self.db.flush()
        return orden

    async def aprobar_orden(self, *, empresa_id: UUID, orden_id: UUID) -> OrdenCompra:
        orden = await self._get_orden_for_update(empresa_id, orden_id)
        if orden.estado != "BORRADOR":
            raise ValueError("Solo una orden en BORRADOR puede aprobarse")
        orden.estado = "APROBADA"
        await self.db.flush()
        return await self.obtener_orden(empresa_id=empresa_id, orden_id=orden_id)

    async def recibir_orden(self, *, empresa_id: UUID, orden_id: UUID, payload: RecepcionCompraCreate) -> RecepcionCompra:
        async with self.db.begin_nested():
            orden = await self._get_orden_for_update(empresa_id, orden_id)
            if orden.estado not in {"APROBADA", "PARCIAL"}:
                raise ValueError("Solo una orden APROBADA o PARCIAL puede recibirse")
            lineas_por_id = {linea.id: linea for linea in orden.lineas}
            inventory = InventoryService(self.db)
            recepcion = RecepcionCompra(
                empresa_id=empresa_id,
                sucursal_id=orden.sucursal_id,
                orden_id=orden.id,
                folio=payload.folio,
                estado="RECIBIDA",
                total=Decimal("0"),
            )
            self.db.add(recepcion)
            await self.db.flush()
            total = Decimal("0")
            for item in payload.lineas:
                linea = lineas_por_id.get(item.orden_linea_id)
                if linea is None:
                    raise ValueError("La línea recibida no pertenece a la orden")
                pendiente = linea.cantidad - linea.cantidad_recibida
                if item.cantidad > pendiente:
                    raise ValueError("La cantidad recibida supera la cantidad pendiente")
                importe = item.cantidad * linea.costo_unitario
                await inventory.entrada(
                    empresa_id=empresa_id,
                    sucursal_id=orden.sucursal_id,
                    producto_id=linea.producto_id,
                    cantidad=item.cantidad,
                    costo_unitario=linea.costo_unitario,
                    origen="RECEPCION_COMPRA",
                    referencia=payload.folio,
                    lote=item.lote,
                    numero_serie=item.numero_serie,
                )
                linea.cantidad_recibida += item.cantidad
                total += importe
                recepcion.lineas.append(
                    RecepcionCompraLinea(
                        orden_linea_id=linea.id,
                        producto_id=linea.producto_id,
                        cantidad=item.cantidad,
                        costo_unitario=linea.costo_unitario,
                        importe=importe,
                        lote=item.lote,
                        numero_serie=item.numero_serie,
                    )
                )
            if total <= 0:
                raise ValueError("La recepción debe tener importe positivo")
            asiento = await AccountingEngine(self.db).handle_compra_recibida(
                empresa_id=empresa_id,
                fecha=(recepcion.fecha or datetime.now(timezone.utc)).date(),
                referencia=payload.folio,
                total=total,
                cuenta_inventario=payload.cuenta_inventario,
                cuenta_cxp=payload.cuenta_cxp,
            )
            recepcion.total = total
            recepcion.asiento_id = asiento.id
            orden.estado = "RECIBIDA" if all(l.cantidad_recibida == l.cantidad for l in orden.lineas) else "PARCIAL"
            await OutboxService(self.db).enqueue(
                empresa_id=empresa_id,
                payload=OutboxEventCreate(
                    aggregate_type="RecepcionCompra",
                    aggregate_id=str(recepcion.id),
                    event_type="CompraRecibida",
                    payload={"recepcion_id": str(recepcion.id), "orden_id": str(orden.id), "folio": recepcion.folio, "total": str(total)},
                    idempotency_key=f"recepcion-compra:{recepcion.id}:recibida",
                ),
            )
            await self.db.flush()
        return await self.obtener_recepcion(empresa_id=empresa_id, recepcion_id=recepcion.id)

    async def obtener_orden(self, *, empresa_id: UUID, orden_id: UUID) -> OrdenCompra:
        result = await self.db.execute(select(OrdenCompra).options(selectinload(OrdenCompra.lineas)).where(OrdenCompra.empresa_id == empresa_id, OrdenCompra.id == orden_id))
        orden = result.scalar_one_or_none()
        if orden is None:
            raise ValueError("Orden de compra inexistente")
        return orden

    async def obtener_recepcion(self, *, empresa_id: UUID, recepcion_id: UUID) -> RecepcionCompra:
        result = await self.db.execute(select(RecepcionCompra).options(selectinload(RecepcionCompra.lineas)).where(RecepcionCompra.empresa_id == empresa_id, RecepcionCompra.id == recepcion_id))
        recepcion = result.scalar_one_or_none()
        if recepcion is None:
            raise ValueError("Recepción de compra inexistente")
        return recepcion

    async def _resolver_proveedor(self, empresa_id: UUID, payload: OrdenCompraCreate) -> Proveedor:
        if payload.proveedor_id:
            proveedor = await self.db.get(Proveedor, payload.proveedor_id)
            if proveedor is None or proveedor.empresa_id != empresa_id:
                raise ValueError("Proveedor inexistente para la empresa")
            return proveedor
        proveedor = Proveedor(empresa_id=empresa_id, **payload.proveedor.model_dump())
        self.db.add(proveedor)
        await self.db.flush()
        return proveedor

    async def _get_producto(self, empresa_id: UUID, producto_id: UUID) -> Producto:
        producto = await self.db.get(Producto, producto_id)
        if producto is None or producto.empresa_id != empresa_id:
            raise ValueError("Producto inexistente para la empresa")
        return producto

    async def _get_orden_for_update(self, empresa_id: UUID, orden_id: UUID) -> OrdenCompra:
        result = await self.db.execute(select(OrdenCompra).options(selectinload(OrdenCompra.lineas)).where(OrdenCompra.empresa_id == empresa_id, OrdenCompra.id == orden_id).with_for_update())
        orden = result.scalar_one_or_none()
        if orden is None:
            raise ValueError("Orden de compra inexistente")
        return orden
