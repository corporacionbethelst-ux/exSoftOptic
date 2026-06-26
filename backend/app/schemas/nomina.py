from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmpleadoCreate(BaseModel):
    sucursal_id: UUID | None = None
    numero_empleado: str = Field(..., min_length=1, max_length=40)
    nombre: str = Field(..., min_length=1, max_length=200)
    email: EmailStr | None = None
    rfc: str | None = Field(None, max_length=20)
    curp: str | None = Field(None, max_length=25)
    nss: str | None = Field(None, max_length=20)
    fecha_ingreso: date
    salario_diario: Decimal = Field(..., gt=0)


class EmpleadoResponse(EmpleadoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    estado: str


class NominaPeriodoCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=40)
    fecha_inicio: date
    fecha_fin: date
    observaciones: str | None = None


class NominaConfirmarRequest(BaseModel):
    cuenta_gasto_sueldos: str = "601.01"
    cuenta_bancos: str = "102.01"
    cuenta_retenciones: str = "216.01"


class NominaReciboResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empleado_id: UUID
    dias_pagados: Decimal
    percepciones: Decimal
    deducciones: Decimal
    neto: Decimal
    estado: str


class NominaPeriodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    folio: str
    fecha_inicio: date
    fecha_fin: date
    estado: str
    total_percepciones: Decimal
    total_deducciones: Decimal
    total_neto: Decimal
    asiento_id: UUID | None
    observaciones: str | None
    recibos: list[NominaReciboResponse] = []
