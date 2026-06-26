from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CitaOpticaCreate(BaseModel):
    sucursal_id: UUID
    cliente_id: UUID
    paciente_id: UUID | None = None
    optometrista_id: UUID | None = None
    folio: str = Field(..., min_length=1, max_length=40)
    fecha_inicio: datetime
    fecha_fin: datetime
    tipo: str = Field(default="EXAMEN_VISUAL", min_length=1, max_length=40)
    motivo: str | None = Field(None, max_length=250)
    observaciones: str | None = None

    @model_validator(mode="after")
    def validar_rango_fechas(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValueError("La fecha fin debe ser posterior a la fecha inicio")
        return self


class CitaOpticaResponse(CitaOpticaCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    estado: str
    created_at: datetime


class RecordatorioClienteCreate(BaseModel):
    cliente_id: UUID
    paciente_id: UUID | None = None
    cita_id: UUID | None = None
    tipo: str = Field(..., min_length=1, max_length=40)
    canal: str = Field(default="EMAIL", min_length=1, max_length=30)
    programado_para: datetime
    mensaje: str = Field(..., min_length=1)


class RecordatorioClienteResponse(RecordatorioClienteCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    estado: str
    created_at: datetime
