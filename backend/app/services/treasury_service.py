from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import AsientoContable, CuentaContable, LineaAsientoContable
from app.models.tesoreria import ConciliacionBancaria, CuentaBancaria, MovimientoBancario
from app.schemas.tesoreria import ConciliarMovimientoRequest, CuentaBancariaCreate, MovimientoBancarioCreate


class TreasuryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def crear_cuenta_bancaria(self, *, empresa_id: UUID, payload: CuentaBancariaCreate) -> CuentaBancaria:
        cuenta = await self.db.get(CuentaContable, payload.cuenta_contable_id)
        if cuenta is None or cuenta.empresa_id != empresa_id:
            raise ValueError("Cuenta contable inexistente para la empresa")
        cuenta_bancaria = CuentaBancaria(empresa_id=empresa_id, **payload.model_dump())
        self.db.add(cuenta_bancaria)
        await self.db.flush()
        return cuenta_bancaria

    async def registrar_movimiento(self, *, empresa_id: UUID, payload: MovimientoBancarioCreate) -> MovimientoBancario:
        cuenta = await self.db.get(CuentaBancaria, payload.cuenta_bancaria_id)
        if cuenta is None or cuenta.empresa_id != empresa_id:
            raise ValueError("Cuenta bancaria inexistente")
        movimiento = MovimientoBancario(empresa_id=empresa_id, estado="PENDIENTE", **payload.model_dump())
        self.db.add(movimiento)
        await self.db.flush()
        return movimiento

    async def conciliar_movimiento(self, *, empresa_id: UUID, payload: ConciliarMovimientoRequest) -> ConciliacionBancaria:
        movimiento = await self.db.get(MovimientoBancario, payload.movimiento_id)
        if movimiento is None or movimiento.empresa_id != empresa_id:
            raise ValueError("Movimiento bancario inexistente")
        if movimiento.estado == "CONCILIADO":
            raise ValueError("Movimiento ya conciliado")
        asiento = await self.db.get(AsientoContable, payload.asiento_id)
        if asiento is None or asiento.empresa_id != empresa_id:
            raise ValueError("Asiento contable inexistente")
        monto_asiento = await self._monto_asiento(asiento.id)
        if abs(Decimal(movimiento.monto)) != monto_asiento:
            raise ValueError("El monto del movimiento no coincide con el asiento")
        conciliacion = ConciliacionBancaria(
            empresa_id=empresa_id,
            cuenta_bancaria_id=movimiento.cuenta_bancaria_id,
            movimiento_id=movimiento.id,
            asiento_id=asiento.id,
            observaciones=payload.observaciones,
        )
        movimiento.asiento_id = asiento.id
        movimiento.estado = "CONCILIADO"
        movimiento.conciliado_en = datetime.now(timezone.utc)
        self.db.add(conciliacion)
        await self.db.flush()
        return conciliacion

    async def listar_movimientos_pendientes(self, *, empresa_id: UUID, cuenta_bancaria_id: UUID | None = None) -> list[MovimientoBancario]:
        query = select(MovimientoBancario).where(MovimientoBancario.empresa_id == empresa_id, MovimientoBancario.estado == "PENDIENTE")
        if cuenta_bancaria_id:
            query = query.where(MovimientoBancario.cuenta_bancaria_id == cuenta_bancaria_id)
        result = await self.db.execute(query.order_by(MovimientoBancario.fecha.asc(), MovimientoBancario.created_at.asc()))
        return result.scalars().all()

    async def _monto_asiento(self, asiento_id: UUID) -> Decimal:
        result = await self.db.execute(select(func.coalesce(func.sum(LineaAsientoContable.debe), 0)).where(LineaAsientoContable.asiento_id == asiento_id))
        return Decimal(result.scalar_one())
