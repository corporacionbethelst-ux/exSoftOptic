from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ImpuestoCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=40)
    nombre: str = Field(..., min_length=1, max_length=120)
    tipo: str = Field(..., min_length=1, max_length=30)
    tasa: Decimal = Field(..., ge=0)
    cuenta_contable_codigo: str | None = Field(None, max_length=50)
    es_retencion: bool = False


class ImpuestoResponse(ImpuestoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    created_at: datetime


class SerieFolioCreate(BaseModel):
    sucursal_id: UUID | None = None
    documento: str = Field(..., min_length=1, max_length=40)
    serie: str = Field(..., min_length=1, max_length=20)
    folio_actual: Decimal = Field(default=Decimal("0"), ge=0)
    formato: str = Field(default="{serie}-{folio:06d}", min_length=1, max_length=80)


class SerieFolioResponse(SerieFolioCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    created_at: datetime


class TipoCambioCreate(BaseModel):
    moneda_origen: str = Field(..., min_length=3, max_length=3)
    moneda_destino: str = Field(..., min_length=3, max_length=3)
    fecha: date
    tasa: Decimal = Field(..., gt=0)
    fuente: str | None = Field(None, max_length=80)


class TipoCambioResponse(TipoCambioCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    created_at: datetime


class ReglaContableCreate(BaseModel):
    evento: str = Field(..., min_length=1, max_length=80)
    descripcion: str = Field(..., min_length=1, max_length=250)
    cuentas: dict = Field(default_factory=dict)
    condiciones: dict = Field(default_factory=dict)


class ReglaContableResponse(ReglaContableCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    created_at: datetime
