from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.laboratorio import ControlCalidadLaboratorio, ConsumoMaterialLaboratorio, OrdenLaboratorio, OrdenLaboratorioEtapa
from app.models.venta import Venta
from app.schemas.laboratorio import ControlCalidadCreate, ConsumoMaterialCreate, OrdenLaboratorioFromVentaCreate
from app.services.inventory_service import InventoryService

ETAPAS_ESTANDAR = ("BLOQUEO", "TALLADO", "PULIDO", "TRATAMIENTO", "MONTAJE", "CONTROL_CALIDAD")


class LabService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_orden_desde_venta(self, *, empresa_id: UUID, venta_id: UUID, payload: OrdenLaboratorioFromVentaCreate) -> OrdenLaboratorio:
        venta = await self._get_venta(empresa_id, venta_id)
        if venta.estado != "CONFIRMADA":
            raise ValueError("Solo una venta CONFIRMADA puede generar orden de laboratorio")
        if venta.paciente_id is None:
            raise ValueError("La venta requiere paciente para generar orden de laboratorio")
        orden = OrdenLaboratorio(
            empresa_id=empresa_id,
            sucursal_id=venta.sucursal_id,
            venta_id=venta.id,
            paciente_id=venta.paciente_id,
            receta_id=venta.receta_id,
            folio=payload.folio,
            prioridad=payload.prioridad,
            estado="PENDIENTE",
            fecha_prometida=payload.fecha_prometida,
            observaciones=payload.observaciones,
        )
        self.db.add(orden)
        await self.db.flush()
        for etapa in ETAPAS_ESTANDAR:
            orden.etapas.append(OrdenLaboratorioEtapa(etapa=etapa, estado="PENDIENTE"))
        await self.db.flush()
        return await self.obtener_orden(empresa_id=empresa_id, orden_id=orden.id)

    async def iniciar_orden(self, *, empresa_id: UUID, orden_id: UUID, responsable_id: UUID | None = None) -> OrdenLaboratorio:
        orden = await self._get_orden_for_update(empresa_id, orden_id)
        if orden.estado != "PENDIENTE":
            raise ValueError("Solo una orden PENDIENTE puede iniciarse")
        now = datetime.now(timezone.utc)
        orden.estado = "EN_PROCESO"
        orden.fecha_inicio = now
        primera = sorted(orden.etapas, key=lambda item: item.created_at or now)[0]
        primera.estado = "EN_PROCESO"
        primera.fecha_inicio = now
        primera.responsable_id = responsable_id
        await self.db.flush()
        return await self.obtener_orden(empresa_id=empresa_id, orden_id=orden_id)

    async def registrar_consumo_material(self, *, empresa_id: UUID, orden_id: UUID, payload: ConsumoMaterialCreate) -> ConsumoMaterialLaboratorio:
        async with self.db.begin_nested():
            orden = await self._get_orden_for_update(empresa_id, orden_id)
            if orden.estado != "EN_PROCESO":
                raise ValueError("Solo una orden EN_PROCESO puede consumir materiales")
            movimiento, costo_total = await InventoryService(self.db).salida_peps(
                empresa_id=empresa_id,
                sucursal_id=orden.sucursal_id,
                producto_id=payload.producto_id,
                cantidad=payload.cantidad,
                origen="LABORATORIO",
                referencia=orden.folio,
            )
            consumo = ConsumoMaterialLaboratorio(
                orden_id=orden.id,
                producto_id=payload.producto_id,
                kardex_movimiento_id=movimiento.id,
                cantidad=payload.cantidad,
                costo_total=costo_total,
                observaciones=payload.observaciones,
            )
            self.db.add(consumo)
            await self.db.flush()
            return consumo

    async def completar_etapa(self, *, empresa_id: UUID, orden_id: UUID, etapa_id: UUID, observaciones: str | None = None) -> OrdenLaboratorio:
        orden = await self._get_orden_for_update(empresa_id, orden_id)
        if orden.estado != "EN_PROCESO":
            raise ValueError("Solo una orden EN_PROCESO puede avanzar etapas")
        etapa = next((item for item in orden.etapas if item.id == etapa_id), None)
        if etapa is None:
            raise ValueError("Etapa inexistente para la orden")
        if etapa.estado != "EN_PROCESO":
            raise ValueError("Solo la etapa EN_PROCESO puede completarse")
        now = datetime.now(timezone.utc)
        etapa.estado = "COMPLETADA"
        etapa.fecha_fin = now
        etapa.observaciones = observaciones
        pendientes = [item for item in sorted(orden.etapas, key=lambda item: item.created_at or now) if item.estado == "PENDIENTE"]
        if pendientes:
            pendientes[0].estado = "EN_PROCESO"
            pendientes[0].fecha_inicio = now
        else:
            orden.estado = "CONTROL_CALIDAD"
            orden.fecha_terminada = now
        await self.db.flush()
        return await self.obtener_orden(empresa_id=empresa_id, orden_id=orden_id)

    async def registrar_control_calidad(self, *, empresa_id: UUID, orden_id: UUID, payload: ControlCalidadCreate, usuario_id: UUID | None = None) -> OrdenLaboratorio:
        orden = await self._get_orden_for_update(empresa_id, orden_id)
        if orden.estado not in {"CONTROL_CALIDAD", "EN_PROCESO"}:
            raise ValueError("La orden no está lista para control de calidad")
        control = ControlCalidadLaboratorio(
            orden_id=orden.id,
            resultado=payload.resultado,
            motivo_rechazo=payload.motivo_rechazo,
            observaciones=payload.observaciones,
            usuario_id=usuario_id,
        )
        self.db.add(control)
        if payload.resultado == "APROBADO":
            orden.estado = "LISTA_ENTREGA"
        elif payload.resultado == "RETRABAJO":
            orden.estado = "EN_PROCESO"
        else:
            orden.estado = "RECHAZADA"
        await self.db.flush()
        return await self.obtener_orden(empresa_id=empresa_id, orden_id=orden_id)

    async def entregar_orden(self, *, empresa_id: UUID, orden_id: UUID) -> OrdenLaboratorio:
        orden = await self._get_orden_for_update(empresa_id, orden_id)
        if orden.estado != "LISTA_ENTREGA":
            raise ValueError("Solo una orden LISTA_ENTREGA puede entregarse")
        orden.estado = "ENTREGADA"
        orden.fecha_entrega = datetime.now(timezone.utc)
        await self.db.flush()
        return await self.obtener_orden(empresa_id=empresa_id, orden_id=orden_id)

    async def obtener_orden(self, *, empresa_id: UUID, orden_id: UUID) -> OrdenLaboratorio:
        result = await self.db.execute(
            select(OrdenLaboratorio)
            .options(
                selectinload(OrdenLaboratorio.etapas),
                selectinload(OrdenLaboratorio.consumos),
                selectinload(OrdenLaboratorio.controles_calidad),
            )
            .where(OrdenLaboratorio.empresa_id == empresa_id, OrdenLaboratorio.id == orden_id)
        )
        orden = result.scalar_one_or_none()
        if orden is None:
            raise ValueError("Orden de laboratorio inexistente")
        return orden

    async def listar_ordenes(self, *, empresa_id: UUID, skip: int = 0, limit: int = 50) -> list[OrdenLaboratorio]:
        result = await self.db.execute(
            select(OrdenLaboratorio)
            .options(selectinload(OrdenLaboratorio.etapas))
            .where(OrdenLaboratorio.empresa_id == empresa_id)
            .order_by(OrdenLaboratorio.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def _get_venta(self, empresa_id: UUID, venta_id: UUID) -> Venta:
        venta = await self.db.get(Venta, venta_id)
        if venta is None or venta.empresa_id != empresa_id:
            raise ValueError("Venta inexistente para la empresa")
        return venta

    async def _get_orden_for_update(self, empresa_id: UUID, orden_id: UUID) -> OrdenLaboratorio:
        result = await self.db.execute(
            select(OrdenLaboratorio)
            .options(selectinload(OrdenLaboratorio.etapas))
            .where(OrdenLaboratorio.empresa_id == empresa_id, OrdenLaboratorio.id == orden_id)
            .with_for_update()
        )
        orden = result.scalar_one_or_none()
        if orden is None:
            raise ValueError("Orden de laboratorio inexistente")
        return orden
