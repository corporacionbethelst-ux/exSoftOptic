from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CuentaBancariaCreate(BaseModel):
    cuenta_contable_id: UUID
    banco: str = Field(..., min_length=1, max_length=120)
    numero_cuenta: str = Field(..., min_length=1, max_length=80)
    moneda: str = Field(default="MXN", min_length=3, max_length=3)


class CuentaBancariaResponse(CuentaBancariaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    estado: str


class MovimientoBancarioCreate(BaseModel):
    cuenta_bancaria_id: UUID
    fecha: date
    referencia: str = Field(..., min_length=1, max_length=120)
    descripcion: str | None = Field(None, max_length=300)
    monto: Decimal
    tipo: str = Field(..., pattern="^(CARGO|ABONO)$")


class MovimientoBancarioResponse(MovimientoBancarioCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    asiento_id: UUID | None
    estado: str
    conciliado_en: datetime | None


class ConciliarMovimientoRequest(BaseModel):
    movimiento_id: UUID
    asiento_id: UUID
    observaciones: str | None = None


class ConciliacionBancariaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    cuenta_bancaria_id: UUID
    movimiento_id: UUID
    asiento_id: UUID
    fecha: datetime
    estado: str
    observaciones: str | None
