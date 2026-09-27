from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditoriaEventoCreate(BaseModel):
    accion: str = Field(..., min_length=1, max_length=80)
    entidad: str = Field(..., min_length=1, max_length=120)
    entidad_id: str | None = Field(None, max_length=80)
    payload: dict = Field(default_factory=dict)
    descripcion: str | None = None


class AuditoriaEventoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID | None
    usuario_id: UUID | None
    secuencia: int
    accion: str
    entidad: str
    entidad_id: str | None
    ip_address: str | None
    user_agent: str | None
    payload: dict
    previous_hash: str | None
    event_hash: str
    descripcion: str | None
    created_at: datetime
