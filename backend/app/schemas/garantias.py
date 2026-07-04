from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GarantiaCreate(BaseModel):
    venta_id: UUID
    orden_laboratorio_id: UUID | None = None
    folio: str = Field(..., min_length=1, max_length=40)
    tipo: str = Field(..., pattern="^(ARMAZON|LENTE|TRATAMIENTO|SERVICIO)$")
    fecha_inicio: date
    fecha_fin: date
    descripcion: str | None = None
    condiciones: str | None = None


class GarantiaFromOrdenCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=40)
    tipo: str = Field(..., pattern="^(ARMAZON|LENTE|TRATAMIENTO|SERVICIO)$")
    fecha_inicio: date
    fecha_fin: date
    descripcion: str | None = None
    condiciones: str | None = None


class ReclamacionGarantiaCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=40)
    motivo: str = Field(..., min_length=1, max_length=300)


class ResolverReclamacionRequest(BaseModel):
    estado: str = Field(..., pattern="^(APROBADA|RECHAZADA|CERRADA)$")
    resolucion: str = Field(..., min_length=1)


class ReclamacionGarantiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    garantia_id: UUID
    folio: str
    motivo: str
    estado: str
    resolucion: str | None
    fecha_cierre: datetime | None


class EventoGarantiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tipo_evento: str
    descripcion: str
    fecha: datetime


class GarantiaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    venta_id: UUID
    orden_laboratorio_id: UUID | None
    paciente_id: UUID | None
    folio: str
    tipo: str
    estado: str
    fecha_inicio: date
    fecha_fin: date
    descripcion: str | None
    condiciones: str | None
    reclamaciones: list[ReclamacionGarantiaResponse] = []
    eventos: list[EventoGarantiaResponse] = []
