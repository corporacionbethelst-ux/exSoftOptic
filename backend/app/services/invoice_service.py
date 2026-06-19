from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.factura import Factura, FacturaEvento, FacturaLinea
from app.models.venta import Venta
from app.schemas.facturacion import FacturaCancelarRequest, FacturaEmitirRequest
from app.schemas.outbox import OutboxEventCreate
from app.services.einvoicing_provider import EInvoiceLine, EInvoicePayload, get_einvoicing_provider
from app.services.outbox_service import OutboxService


class InvoiceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def emitir_desde_venta(self, *, empresa_id: UUID, payload: FacturaEmitirRequest) -> Factura:
        async with self.db.begin_nested():
            venta = await self._get_venta(empresa_id, payload.venta_id)
            if venta.estado != "CONFIRMADA":
                raise ValueError("Solo una venta CONFIRMADA puede facturarse")
            if not venta.lineas:
                raise ValueError("La venta no tiene líneas facturables")
            factura = Factura(
                empresa_id=empresa_id,
                sucursal_id=venta.sucursal_id,
                venta_id=venta.id,
                cliente_id=venta.cliente_id,
                folio=payload.folio,
                estado="BORRADOR",
                moneda=payload.moneda,
                subtotal=venta.subtotal,
                impuestos=venta.impuestos,
                total=venta.total,
                proveedor=payload.proveedor.upper(),
            )
            self.db.add(factura)
            await self.db.flush()
            for linea in venta.lineas:
                factura.lineas.append(
                    FacturaLinea(
                        producto_id=linea.producto_id,
                        descripcion=linea.descripcion,
                        cantidad=linea.cantidad,
                        precio_unitario=linea.precio_unitario,
                        descuento=linea.descuento,
                        importe=linea.importe,
                    )
                )
            await self.db.flush()
            provider = get_einvoicing_provider(factura.proveedor)
            result = await provider.issue_invoice(
                EInvoicePayload(
                    empresa_id=empresa_id,
                    venta_id=venta.id,
                    folio=factura.folio,
                    moneda=factura.moneda,
                    subtotal=factura.subtotal,
                    impuestos=factura.impuestos,
                    total=factura.total,
                    lineas=[
                        EInvoiceLine(
                            producto_id=linea.producto_id,
                            descripcion=linea.descripcion,
                            cantidad=linea.cantidad,
                            precio_unitario=linea.precio_unitario,
                            descuento=linea.descuento,
                            importe=linea.importe,
                        )
                        for linea in factura.lineas
                    ],
                )
            )
            factura.uuid_fiscal = result.uuid_fiscal
            factura.xml_url = result.xml_url
            factura.pdf_url = result.pdf_url
            factura.fecha_timbrado = datetime.now(timezone.utc)
            factura.estado = "TIMBRADA"
            await self._evento(factura.id, "FACTURA_TIMBRADA", f"Factura timbrada con UUID {result.uuid_fiscal}")
            await OutboxService(self.db).enqueue(
                empresa_id=empresa_id,
                payload=OutboxEventCreate(
                    aggregate_type="Factura",
                    aggregate_id=str(factura.id),
                    event_type="FacturaTimbrada",
                    payload={"factura_id": str(factura.id), "venta_id": str(venta.id), "folio": factura.folio, "uuid_fiscal": result.uuid_fiscal, "total": str(factura.total)},
                    idempotency_key=f"factura:{factura.id}:timbrada",
                ),
            )
            await self.db.flush()
        return await self.obtener_factura(empresa_id=empresa_id, factura_id=factura.id)

    async def cancelar_factura(self, *, empresa_id: UUID, factura_id: UUID, payload: FacturaCancelarRequest) -> Factura:
        async with self.db.begin_nested():
            factura = await self._get_factura_for_update(empresa_id, factura_id)
            if factura.estado != "TIMBRADA":
                raise ValueError("Solo una factura TIMBRADA puede cancelarse")
            provider = get_einvoicing_provider(factura.proveedor)
            await provider.cancel_invoice(factura.uuid_fiscal, payload.motivo)
            factura.estado = "CANCELADA"
            await self._evento(factura.id, "FACTURA_CANCELADA", payload.motivo)
            await OutboxService(self.db).enqueue(
                empresa_id=empresa_id,
                payload=OutboxEventCreate(
                    aggregate_type="Factura",
                    aggregate_id=str(factura.id),
                    event_type="FacturaCancelada",
                    payload={"factura_id": str(factura.id), "folio": factura.folio, "uuid_fiscal": factura.uuid_fiscal, "motivo": payload.motivo},
                    idempotency_key=f"factura:{factura.id}:cancelada",
                ),
            )
            await self.db.flush()
        return await self.obtener_factura(empresa_id=empresa_id, factura_id=factura_id)

    async def obtener_factura(self, *, empresa_id: UUID, factura_id: UUID) -> Factura:
        result = await self.db.execute(
            select(Factura)
            .options(selectinload(Factura.lineas), selectinload(Factura.eventos))
            .where(Factura.empresa_id == empresa_id, Factura.id == factura_id)
        )
        factura = result.scalar_one_or_none()
        if factura is None:
            raise ValueError("Factura inexistente")
        return factura

    async def _get_venta(self, empresa_id: UUID, venta_id: UUID) -> Venta:
        result = await self.db.execute(select(Venta).options(selectinload(Venta.lineas)).where(Venta.empresa_id == empresa_id, Venta.id == venta_id))
        venta = result.scalar_one_or_none()
        if venta is None:
            raise ValueError("Venta inexistente")
        return venta

    async def _get_factura_for_update(self, empresa_id: UUID, factura_id: UUID) -> Factura:
        result = await self.db.execute(select(Factura).where(Factura.empresa_id == empresa_id, Factura.id == factura_id).with_for_update())
        factura = result.scalar_one_or_none()
        if factura is None:
            raise ValueError("Factura inexistente")
        return factura

    async def _evento(self, factura_id: UUID, tipo_evento: str, descripcion: str) -> None:
        self.db.add(FacturaEvento(factura_id=factura_id, tipo_evento=tipo_evento, descripcion=descripcion))
        await self.db.flush()
