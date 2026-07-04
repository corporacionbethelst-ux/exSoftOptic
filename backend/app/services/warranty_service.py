from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.garantia import EventoGarantia, Garantia, ReclamacionGarantia
from app.models.laboratorio import OrdenLaboratorio
from app.models.venta import Venta
from app.schemas.garantias import GarantiaCreate, GarantiaFromOrdenCreate, ReclamacionGarantiaCreate, ResolverReclamacionRequest


class WarrantyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_garantia(self, *, empresa_id: UUID, payload: GarantiaCreate) -> Garantia:
        venta = await self._get_venta(empresa_id, payload.venta_id)
        if venta.estado != "CONFIRMADA":
            raise ValueError("Solo una venta CONFIRMADA puede generar garantía")
        if payload.fecha_fin < payload.fecha_inicio:
            raise ValueError("La fecha fin de garantía no puede ser anterior al inicio")
        garantia = Garantia(
            empresa_id=empresa_id,
            sucursal_id=venta.sucursal_id,
            venta_id=venta.id,
            orden_laboratorio_id=payload.orden_laboratorio_id,
            paciente_id=venta.paciente_id,
            folio=payload.folio,
            tipo=payload.tipo,
            estado="ACTIVA",
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            descripcion=payload.descripcion,
            condiciones=payload.condiciones,
        )
        self.db.add(garantia)
        await self.db.flush()
        await self._evento(garantia.id, None, "GARANTIA_CREADA", "Garantía creada")
        return await self.obtener_garantia(empresa_id=empresa_id, garantia_id=garantia.id)

    async def crear_desde_orden_laboratorio(self, *, empresa_id: UUID, orden_id: UUID, payload: GarantiaFromOrdenCreate) -> Garantia:
        orden = await self.db.get(OrdenLaboratorio, orden_id)
        if orden is None or orden.empresa_id != empresa_id:
            raise ValueError("Orden de laboratorio inexistente para la empresa")
        if orden.estado != "ENTREGADA":
            raise ValueError("Solo una orden ENTREGADA puede generar garantía")
        return await self.crear_garantia(
            empresa_id=empresa_id,
            payload=GarantiaCreate(
                venta_id=orden.venta_id,
                orden_laboratorio_id=orden.id,
                folio=payload.folio,
                tipo=payload.tipo,
                fecha_inicio=payload.fecha_inicio,
                fecha_fin=payload.fecha_fin,
                descripcion=payload.descripcion,
                condiciones=payload.condiciones,
            ),
        )

    async def abrir_reclamacion(self, *, empresa_id: UUID, garantia_id: UUID, payload: ReclamacionGarantiaCreate) -> ReclamacionGarantia:
        garantia = await self._get_garantia_for_update(empresa_id, garantia_id)
        await self._actualizar_estado_vencida(garantia)
        if garantia.estado != "ACTIVA":
            raise ValueError("Solo una garantía ACTIVA puede recibir reclamaciones")
        reclamacion = ReclamacionGarantia(
            empresa_id=empresa_id,
            garantia_id=garantia.id,
            folio=payload.folio,
            motivo=payload.motivo,
            estado="ABIERTA",
        )
        garantia.estado = "EN_RECLAMO"
        self.db.add(reclamacion)
        await self.db.flush()
        await self._evento(garantia.id, reclamacion.id, "RECLAMACION_ABIERTA", payload.motivo)
        return reclamacion

    async def resolver_reclamacion(self, *, empresa_id: UUID, reclamacion_id: UUID, payload: ResolverReclamacionRequest) -> Garantia:
        result = await self.db.execute(
            select(ReclamacionGarantia)
            .join(Garantia, Garantia.id == ReclamacionGarantia.garantia_id)
            .where(ReclamacionGarantia.id == reclamacion_id, Garantia.empresa_id == empresa_id)
            .with_for_update()
        )
        reclamacion = result.scalar_one_or_none()
        if reclamacion is None:
            raise ValueError("Reclamación inexistente")
        if reclamacion.estado != "ABIERTA":
            raise ValueError("Solo una reclamación ABIERTA puede resolverse")
        reclamacion.estado = payload.estado
        reclamacion.resolucion = payload.resolucion
        reclamacion.fecha_cierre = datetime.now(timezone.utc)
        garantia = await self._get_garantia_for_update(empresa_id, reclamacion.garantia_id)
        garantia.estado = "ACTIVA" if payload.estado in {"RECHAZADA", "CERRADA"} else "EN_RECLAMO"
        await self._evento(garantia.id, reclamacion.id, "RECLAMACION_RESUELTA", payload.resolucion)
        await self.db.flush()
        return await self.obtener_garantia(empresa_id=empresa_id, garantia_id=garantia.id)

    async def obtener_garantia(self, *, empresa_id: UUID, garantia_id: UUID) -> Garantia:
        result = await self.db.execute(
            select(Garantia)
            .options(selectinload(Garantia.reclamaciones), selectinload(Garantia.eventos))
            .where(Garantia.empresa_id == empresa_id, Garantia.id == garantia_id)
        )
        garantia = result.scalar_one_or_none()
        if garantia is None:
            raise ValueError("Garantía inexistente")
        await self._actualizar_estado_vencida(garantia)
        return garantia

    async def _get_venta(self, empresa_id: UUID, venta_id: UUID) -> Venta:
        venta = await self.db.get(Venta, venta_id)
        if venta is None or venta.empresa_id != empresa_id:
            raise ValueError("Venta inexistente para la empresa")
        return venta

    async def _get_garantia_for_update(self, empresa_id: UUID, garantia_id: UUID) -> Garantia:
        result = await self.db.execute(select(Garantia).where(Garantia.empresa_id == empresa_id, Garantia.id == garantia_id).with_for_update())
        garantia = result.scalar_one_or_none()
        if garantia is None:
            raise ValueError("Garantía inexistente")
        return garantia

    async def _actualizar_estado_vencida(self, garantia: Garantia) -> None:
        if garantia.estado == "ACTIVA" and garantia.fecha_fin < datetime.now(timezone.utc).date():
            garantia.estado = "VENCIDA"
            await self.db.flush()

    async def _evento(self, garantia_id: UUID, reclamacion_id: UUID | None, tipo_evento: str, descripcion: str) -> None:
        self.db.add(EventoGarantia(garantia_id=garantia_id, reclamacion_id=reclamacion_id, tipo_evento=tipo_evento, descripcion=descripcion))
        await self.db.flush()
