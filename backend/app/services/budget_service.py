from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.presupuesto import CentroCosto, Presupuesto, PresupuestoLinea
from app.schemas.presupuestos import CentroCostoCreate, ComprometerPresupuestoRequest, PresupuestoCreate


class BudgetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_centro_costo(self, *, empresa_id: UUID, payload: CentroCostoCreate) -> CentroCosto:
        centro = CentroCosto(empresa_id=empresa_id, estado="ACTIVO", **payload.model_dump())
        self.db.add(centro)
        await self.db.flush()
        return centro

    async def crear_presupuesto(self, *, empresa_id: UUID, payload: PresupuestoCreate) -> Presupuesto:
        centro = await self.db.get(CentroCosto, payload.centro_costo_id)
        if centro is None or centro.empresa_id != empresa_id:
            raise ValueError("Centro de costo inexistente")
        presupuesto = Presupuesto(
            empresa_id=empresa_id,
            centro_costo_id=payload.centro_costo_id,
            folio=payload.folio,
            nombre=payload.nombre,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            estado="APROBADO",
            observaciones=payload.observaciones,
        )
        self.db.add(presupuesto)
        await self.db.flush()
        for linea in payload.lineas:
            presupuesto.lineas.append(PresupuestoLinea(cuenta_codigo=linea.cuenta_codigo, monto=linea.monto))
        await self.db.flush()
        return await self.obtener_presupuesto(empresa_id=empresa_id, presupuesto_id=presupuesto.id)

    async def comprometer(self, *, empresa_id: UUID, payload: ComprometerPresupuestoRequest) -> Presupuesto:
        presupuesto = await self._get_presupuesto_for_update(empresa_id, payload.presupuesto_id)
        if presupuesto.estado != "APROBADO":
            raise ValueError("Solo un presupuesto APROBADO puede comprometerse")
        linea = next((item for item in presupuesto.lineas if item.cuenta_codigo == payload.cuenta_codigo), None)
        if linea is None:
            raise ValueError("Cuenta no presupuestada")
        disponible = linea.monto - linea.monto_comprometido - linea.monto_ejercido
        if payload.monto > disponible:
            raise ValueError("Presupuesto insuficiente")
        linea.monto_comprometido += payload.monto
        await self.db.flush()
        return await self.obtener_presupuesto(empresa_id=empresa_id, presupuesto_id=presupuesto.id)

    async def obtener_presupuesto(self, *, empresa_id: UUID, presupuesto_id: UUID) -> Presupuesto:
        result = await self.db.execute(select(Presupuesto).options(selectinload(Presupuesto.lineas)).where(Presupuesto.empresa_id == empresa_id, Presupuesto.id == presupuesto_id))
        presupuesto = result.scalar_one_or_none()
        if presupuesto is None:
            raise ValueError("Presupuesto inexistente")
        return presupuesto

    async def _get_presupuesto_for_update(self, empresa_id: UUID, presupuesto_id: UUID) -> Presupuesto:
        result = await self.db.execute(select(Presupuesto).options(selectinload(Presupuesto.lineas)).where(Presupuesto.empresa_id == empresa_id, Presupuesto.id == presupuesto_id).with_for_update())
        presupuesto = result.scalar_one_or_none()
        if presupuesto is None:
            raise ValueError("Presupuesto inexistente")
        return presupuesto
