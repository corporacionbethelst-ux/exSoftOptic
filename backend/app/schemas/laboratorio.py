from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrdenLaboratorioFromVentaCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=40)
    prioridad: str = Field(default="NORMAL", max_length=20)
    fecha_prometida: datetime | None = None
    observaciones: str | None = None


class ConsumoMaterialCreate(BaseModel):
    producto_id: UUID
    cantidad: Decimal = Field(..., gt=0)
    observaciones: str | None = None


class ControlCalidadCreate(BaseModel):
    resultado: str = Field(..., pattern="^(APROBADO|RECHAZADO|RETRABAJO)$")
    motivo_rechazo: str | None = Field(None, max_length=300)
    observaciones: str | None = None


class CompletarEtapaRequest(BaseModel):
    observaciones: str | None = None


class EtapaLaboratorioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    etapa: str
    estado: str
    responsable_id: UUID | None
    fecha_inicio: datetime | None
    fecha_fin: datetime | None
    observaciones: str | None


class ConsumoMaterialResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    producto_id: UUID
    kardex_movimiento_id: UUID | None
    cantidad: Decimal
    costo_total: Decimal
    observaciones: str | None


class ControlCalidadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    resultado: str
    motivo_rechazo: str | None
    observaciones: str | None
    usuario_id: UUID | None
    fecha: datetime


class OrdenLaboratorioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    venta_id: UUID
    paciente_id: UUID
    receta_id: UUID | None
    folio: str
    estado: str
    prioridad: str
    fecha_prometida: datetime | None
    fecha_inicio: datetime | None
    fecha_terminada: datetime | None
    fecha_entrega: datetime | None
    observaciones: str | None
    etapas: list[EtapaLaboratorioResponse] = []
    consumos: list[ConsumoMaterialResponse] = []
    controles_calidad: list[ControlCalidadResponse] = []
