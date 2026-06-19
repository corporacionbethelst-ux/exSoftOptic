from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class ClienteCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=200)
    email: EmailStr | None = None
    telefono: str | None = Field(None, max_length=30)
    rfc: str | None = Field(None, max_length=20)
    codigo_postal: str | None = Field(None, max_length=10)
    regimen_fiscal: str | None = Field(None, max_length=50)


class PacienteCreate(BaseModel):
    cliente_id: UUID | None = None
    nombre: str = Field(..., min_length=1, max_length=200)
    fecha_nacimiento: date | None = None
    telefono: str | None = Field(None, max_length=30)
    email: EmailStr | None = None


class RecetaOpticaCreate(BaseModel):
    paciente_id: UUID | None = None
    fecha: date = Field(default_factory=date.today)
    od_esfera: Decimal | None = None
    od_cilindro: Decimal | None = None
    od_eje: Decimal | None = Field(None, ge=0, le=180)
    od_adicion: Decimal | None = None
    oi_esfera: Decimal | None = None
    oi_cilindro: Decimal | None = None
    oi_eje: Decimal | None = Field(None, ge=0, le=180)
    oi_adicion: Decimal | None = None
    dnp: Decimal | None = Field(None, ge=0)
    altura: Decimal | None = Field(None, ge=0)
    observaciones: str | None = None


class VentaLineaCreate(BaseModel):
    producto_id: UUID
    descripcion: str | None = Field(None, max_length=300)
    cantidad: Decimal = Field(..., gt=0)
    precio_unitario: Decimal = Field(..., ge=0)
    descuento: Decimal = Field(default=Decimal("0"), ge=0)

    @property
    def importe(self) -> Decimal:
        return (self.cantidad * self.precio_unitario) - self.descuento

    @model_validator(mode="after")
    def validar_importe_no_negativo(self):
        if self.importe < 0:
            raise ValueError("El descuento no puede superar el importe bruto de la línea")
        return self


class PagoVentaCreate(BaseModel):
    metodo_pago: str = Field(..., min_length=1, max_length=40)
    monto: Decimal = Field(..., gt=0)
    referencia: str | None = Field(None, max_length=120)


class VentaCreate(BaseModel):
    sucursal_id: UUID
    cliente_id: UUID | None = None
    cliente: ClienteCreate | None = None
    paciente_id: UUID | None = None
    paciente: PacienteCreate | None = None
    receta_id: UUID | None = None
    receta: RecetaOpticaCreate | None = None
    folio: str = Field(..., min_length=1, max_length=40)
    impuestos: Decimal = Field(default=Decimal("0"), ge=0)
    lineas: list[VentaLineaCreate] = Field(..., min_length=1)
    pagos: list[PagoVentaCreate] = Field(default_factory=list)

    @model_validator(mode="after")
    def validar_cliente(self):
        if self.cliente_id is None and self.cliente is None:
            raise ValueError("Se requiere cliente_id o datos de cliente")
        return self


class VentaConfirmarRequest(BaseModel):
    cuenta_cobro: str = "102.01"
    cuenta_ingresos: str = "401.01"
    cuenta_costo_ventas: str = "501.01"
    cuenta_inventario: str = "115.01"


class ClienteResponse(ClienteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID


class PacienteResponse(PacienteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    cliente_id: UUID


class RecetaOpticaResponse(RecetaOpticaCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    paciente_id: UUID


class PagoVentaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    metodo_pago: str
    monto: Decimal
    referencia: str | None
    fecha: datetime


class VentaLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    producto_id: UUID
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    descuento: Decimal
    importe: Decimal
    costo_total: Decimal


class VentaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    cliente_id: UUID
    paciente_id: UUID | None
    receta_id: UUID | None
    asiento_id: UUID | None
    folio: str
    fecha: datetime
    estado: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal
    costo_total: Decimal
    lineas: list[VentaLineaResponse] = []
    pagos: list[PagoVentaResponse] = []


class DevolucionVentaLineaCreate(BaseModel):
    venta_linea_id: UUID
    cantidad: Decimal = Field(..., gt=0)


class DevolucionVentaCreate(BaseModel):
    folio: str = Field(..., min_length=1, max_length=40)
    motivo: str = Field(..., min_length=1, max_length=250)
    lineas: list[DevolucionVentaLineaCreate] = Field(..., min_length=1)
    cuenta_cobro: str = "102.01"
    cuenta_ingresos: str = "401.01"
    cuenta_costo_ventas: str = "501.01"
    cuenta_inventario: str = "115.01"


class DevolucionVentaLineaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    venta_linea_id: UUID
    producto_id: UUID
    cantidad: Decimal
    importe: Decimal
    costo_total: Decimal


class DevolucionVentaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    venta_id: UUID
    asiento_id: UUID | None
    folio: str
    motivo: str
    estado: str
    subtotal: Decimal
    impuestos: Decimal
    total: Decimal
    costo_total: Decimal
    lineas: list[DevolucionVentaLineaResponse] = []
