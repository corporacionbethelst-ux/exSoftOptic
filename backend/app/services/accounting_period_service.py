from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import PeriodoContable
from app.schemas.inventory_accounting import PeriodoContableCreate


class AccountingPeriodService:
    """Administra periodos contables y bloqueo de contabilización por fecha."""

    ESTADO_ABIERTO = "ABIERTO"
    ESTADO_CERRADO = "CERRADO"

    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_periodo(self, *, empresa_id: UUID, payload: PeriodoContableCreate) -> PeriodoContable:
        if payload.fecha_fin < payload.fecha_inicio:
            raise ValueError("La fecha final del periodo no puede ser menor a la inicial")
        overlapping = await self._buscar_solapamiento(empresa_id=empresa_id, fecha_inicio=payload.fecha_inicio, fecha_fin=payload.fecha_fin)
        if overlapping:
            raise ValueError("El periodo contable se solapa con otro periodo existente")
        periodo = PeriodoContable(empresa_id=empresa_id, estado=self.ESTADO_ABIERTO, **payload.model_dump())
        self.db.add(periodo)
        await self.db.flush()
        return periodo

    async def listar_periodos(self, *, empresa_id: UUID, skip: int = 0, limit: int = 100) -> list[PeriodoContable]:
        result = await self.db.execute(
            select(PeriodoContable)
            .where(PeriodoContable.empresa_id == empresa_id)
            .order_by(PeriodoContable.fecha_inicio.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def cambiar_estado(self, *, empresa_id: UUID, periodo_id: UUID, estado: str) -> PeriodoContable:
        if estado not in {self.ESTADO_ABIERTO, self.ESTADO_CERRADO}:
            raise ValueError("Estado de periodo inválido")
        periodo = await self._get_periodo_for_update(empresa_id=empresa_id, periodo_id=periodo_id)
        periodo.estado = estado
        await self.db.flush()
        return periodo

    async def assert_fecha_contabilizable(self, *, empresa_id: UUID, fecha: date) -> None:
        periodo = await self.periodo_para_fecha(empresa_id=empresa_id, fecha=fecha)
        if periodo and periodo.estado == self.ESTADO_CERRADO:
            raise ValueError(f"El periodo contable {periodo.codigo} está cerrado")

    async def periodo_para_fecha(self, *, empresa_id: UUID, fecha: date) -> PeriodoContable | None:
        result = await self.db.execute(
            select(PeriodoContable).where(
                PeriodoContable.empresa_id == empresa_id,
                PeriodoContable.fecha_inicio <= fecha,
                PeriodoContable.fecha_fin >= fecha,
            )
        )
        return result.scalar_one_or_none()

    async def _buscar_solapamiento(self, *, empresa_id: UUID, fecha_inicio: date, fecha_fin: date) -> PeriodoContable | None:
        result = await self.db.execute(
            select(PeriodoContable).where(
                PeriodoContable.empresa_id == empresa_id,
                PeriodoContable.fecha_inicio <= fecha_fin,
                PeriodoContable.fecha_fin >= fecha_inicio,
            )
        )
        return result.scalar_one_or_none()

    async def _get_periodo_for_update(self, *, empresa_id: UUID, periodo_id: UUID) -> PeriodoContable:
        result = await self.db.execute(
            select(PeriodoContable)
            .where(PeriodoContable.empresa_id == empresa_id, PeriodoContable.id == periodo_id)
            .with_for_update()
        )
        periodo = result.scalar_one_or_none()
        if periodo is None:
            raise ValueError("Periodo contable inexistente")
        return periodo
