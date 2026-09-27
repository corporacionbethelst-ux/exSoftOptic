from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CentroCostoCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=40)
    nombre: str = Field(..., min_length=1, max_length=150)
    descripcion: str | None = Field(None, max_length=500)


class CentroCostoResponse(CentroCostoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    estado: str


class PresupuestoLineaCreate(BaseModel):
    cuenta_codigo: str = Field(..., min_length=1, max_length=40)
    monto: Decimal = Field(..., gt=0)


class PresupuestoCreate(BaseModel):
    centro_costo_id: UUID
    folio: str = Field(..., min_length=1, max_length=40)
    nombre: str = Field(..., min_length=1, max_length=180)
    fecha_inicio: date
    fecha_fin: date
    observaciones: str | None = None
    lineas: list[PresupuestoLineaCreate] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validar_periodo(self):
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("La fecha fin no puede ser anterior a la fecha inicio")
        return self


class PresupuestoLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cuenta_codigo: str
    monto: Decimal
    monto_comprometido: Decimal
    monto_ejercido: Decimal


class PresupuestoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    centro_costo_id: UUID
    folio: str
    nombre: str
    fecha_inicio: date
    fecha_fin: date
    estado: str
    observaciones: str | None
    lineas: list[PresupuestoLineaResponse] = []


class ComprometerPresupuestoRequest(BaseModel):
    presupuesto_id: UUID
    cuenta_codigo: str = Field(..., min_length=1, max_length=40)
    monto: Decimal = Field(..., gt=0)
