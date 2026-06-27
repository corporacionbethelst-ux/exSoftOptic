from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FacturaEmitirRequest(BaseModel):
    venta_id: UUID
    folio: str = Field(..., min_length=1, max_length=40)
    proveedor: str = Field(default="MOCK", max_length=60)
    moneda: str = Field(default="MXN", min_length=3, max_length=3)


class FacturaCancelarRequest(BaseModel):
    motivo: str = Field(..., min_length=1, max_length=300)


class FacturaLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    producto_id: UUID
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    descuento: Decimal
    importe: Decimal


class FacturaEventoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    tipo_evento: str
    descripcion: str
    fecha: datetime


class FacturaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    venta_id: UUID
    cliente_id: UUID
    folio: str
    estado: str
    moneda: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal
    proveedor: str
    uuid_fiscal: str | None
    xml_url: str | None
    pdf_url: str | None
    error: str | None
    fecha_timbrado: datetime | None
    lineas: list[FacturaLineaResponse] = []
    eventos: list[FacturaEventoResponse] = []
