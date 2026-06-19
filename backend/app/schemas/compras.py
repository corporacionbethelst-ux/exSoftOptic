from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ProveedorCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    rfc: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    telefono: str | None = Field(None, max_length=30)


class ProveedorResponse(ProveedorCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID


class OrdenCompraLineaCreate(BaseModel):
    producto_id: UUID
    descripcion: str | None = Field(None, max_length=300)
    cantidad: Decimal = Field(..., gt=0)
    costo_unitario: Decimal = Field(..., ge=0)

    @property
    def importe(self) -> Decimal:
        return self.cantidad * self.costo_unitario


class OrdenCompraCreate(BaseModel):
    sucursal_id: UUID
    proveedor_id: UUID | None = None
    proveedor: ProveedorCreate | None = None
    folio: str = Field(..., min_length=1, max_length=40)
    impuestos: Decimal = Field(default=Decimal("0"), ge=0)
    lineas: list[OrdenCompraLineaCreate] = Field(..., min_length=1)

    @model_validator(mode="after")
    def validar_proveedor(self):
        if self.proveedor_id is None and self.proveedor is None:
            raise ValueError("Se requiere proveedor_id o datos de proveedor")
        return self


class RecepcionCompraLineaCreate(BaseModel):
    orden_linea_id: UUID
    cantidad: Decimal = Field(..., gt=0)
    lote: str | None = Field(None, max_length=80)
    numero_serie: str | None = Field(None, max_length=120)


class RecepcionCompraCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=40)
    lineas: list[RecepcionCompraLineaCreate] = Field(..., min_length=1)
    cuenta_inventario: str = "115.01"
    cuenta_cxp: str = "201.01"


class OrdenCompraLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    producto_id: UUID
    descripcion: str
    cantidad: Decimal
    cantidad_recibida: Decimal
    costo_unitario: Decimal
    importe: Decimal


class OrdenCompraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    proveedor_id: UUID
    folio: str
    fecha: datetime
    estado: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal
    lineas: list[OrdenCompraLineaResponse] = []


class RecepcionCompraLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    orden_linea_id: UUID
    producto_id: UUID
    cantidad: Decimal
    costo_unitario: Decimal
    importe: Decimal
    lote: str | None
    numero_serie: str | None


class RecepcionCompraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    orden_id: UUID
    asiento_id: UUID | None
    folio: str
    fecha: datetime
    estado: str
    total: Decimal
    lineas: list[RecepcionCompraLineaResponse] = []


class SolicitudCompraGenerarRequest(BaseModel):
    sucursal_id: UUID
    folio: str = Field(..., min_length=1, max_length=40)
    observaciones: str | None = Field(None, max_length=500)


class SolicitudCompraLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    producto_id: UUID
    cantidad_sugerida: Decimal
    costo_estimado: Decimal
    motivo: str


class SolicitudCompraResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    folio: str
    origen: str
    estado: str
    observaciones: str | None
    lineas: list[SolicitudCompraLineaResponse] = []
