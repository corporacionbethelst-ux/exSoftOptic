from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.nomina import Empleado, NominaPeriodo, NominaRecibo
from app.schemas.nomina import EmpleadoCreate, NominaConfirmarRequest, NominaPeriodoCreate
from app.services.accounting_engine import AccountingEngine


class PayrollService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_empleado(self, *, empresa_id: UUID, payload: EmpleadoCreate) -> Empleado:
        empleado = Empleado(empresa_id=empresa_id, estado="ACTIVO", **payload.model_dump())
        self.db.add(empleado)
        await self.db.flush()
        return empleado

    async def crear_periodo(self, *, empresa_id: UUID, payload: NominaPeriodoCreate) -> NominaPeriodo:
        if payload.fecha_fin < payload.fecha_inicio:
            raise ValueError("La fecha fin no puede ser anterior al inicio")
        periodo = NominaPeriodo(
            empresa_id=empresa_id,
            folio=payload.folio,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            estado="BORRADOR",
            observaciones=payload.observaciones,
        )
        self.db.add(periodo)
        await self.db.flush()
        return await self.obtener_periodo(empresa_id=empresa_id, periodo_id=periodo.id)

    async def calcular_periodo(self, *, empresa_id: UUID, periodo_id: UUID) -> NominaPeriodo:
        periodo = await self._get_periodo_for_update(empresa_id, periodo_id)
        if periodo.estado not in {"BORRADOR", "CALCULADO"}:
            raise ValueError("Solo una nómina BORRADOR o CALCULADA puede recalcularse")
        for recibo in list(periodo.recibos):
            await self.db.delete(recibo)
        await self.db.flush()
        empleados = (await self.db.execute(select(Empleado).where(Empleado.empresa_id == empresa_id, Empleado.estado == "ACTIVO"))).scalars().all()
        dias = Decimal((periodo.fecha_fin - periodo.fecha_inicio).days + 1)
        total_percepciones = Decimal("0")
        total_deducciones = Decimal("0")
        for empleado in empleados:
            percepciones = empleado.salario_diario * dias
            deducciones = Decimal("0")
            neto = percepciones - deducciones
            periodo.recibos.append(
                NominaRecibo(
                    empresa_id=empresa_id,
                    empleado_id=empleado.id,
                    dias_pagados=dias,
                    percepciones=percepciones,
                    deducciones=deducciones,
                    neto=neto,
                    estado="CALCULADO",
                )
            )
            total_percepciones += percepciones
            total_deducciones += deducciones
        periodo.total_percepciones = total_percepciones
        periodo.total_deducciones = total_deducciones
        periodo.total_neto = total_percepciones - total_deducciones
        periodo.estado = "CALCULADO"
        await self.db.flush()
        return await self.obtener_periodo(empresa_id=empresa_id, periodo_id=periodo.id)

    async def confirmar_periodo(self, *, empresa_id: UUID, periodo_id: UUID, payload: NominaConfirmarRequest) -> NominaPeriodo:
        async with self.db.begin_nested():
            periodo = await self._get_periodo_for_update(empresa_id, periodo_id)
            if periodo.estado != "CALCULADO":
                raise ValueError("Solo una nómina CALCULADA puede confirmarse")
            if periodo.total_neto <= 0:
                raise ValueError("La nómina requiere total neto positivo")
            asiento = await AccountingEngine(self.db).handle_nomina_generada(
                empresa_id=empresa_id,
                fecha=periodo.fecha_fin,
                referencia=periodo.folio,
                total_percepciones=periodo.total_percepciones,
                total_deducciones=periodo.total_deducciones,
                total_neto=periodo.total_neto,
                cuenta_gasto_sueldos=payload.cuenta_gasto_sueldos,
                cuenta_bancos=payload.cuenta_bancos,
                cuenta_retenciones=payload.cuenta_retenciones,
            )
            periodo.asiento_id = asiento.id
            periodo.estado = "CONFIRMADO"
            for recibo in periodo.recibos:
                recibo.estado = "CONFIRMADO"
            await self.db.flush()
        return await self.obtener_periodo(empresa_id=empresa_id, periodo_id=periodo_id)

    async def obtener_periodo(self, *, empresa_id: UUID, periodo_id: UUID) -> NominaPeriodo:
        result = await self.db.execute(select(NominaPeriodo).options(selectinload(NominaPeriodo.recibos)).where(NominaPeriodo.empresa_id == empresa_id, NominaPeriodo.id == periodo_id))
        periodo = result.scalar_one_or_none()
        if periodo is None:
            raise ValueError("Periodo de nómina inexistente")
        return periodo

    async def _get_periodo_for_update(self, empresa_id: UUID, periodo_id: UUID) -> NominaPeriodo:
        result = await self.db.execute(select(NominaPeriodo).options(selectinload(NominaPeriodo.recibos)).where(NominaPeriodo.empresa_id == empresa_id, NominaPeriodo.id == periodo_id).with_for_update())
        periodo = result.scalar_one_or_none()
        if periodo is None:
            raise ValueError("Periodo de nómina inexistente")
        return periodo
