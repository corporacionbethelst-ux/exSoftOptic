from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductoCreate(BaseModel):
    categoria_id: UUID | None = None
    marca_id: UUID | None = None
    sku: str = Field(..., min_length=1, max_length=50)
    codigo_barras: str | None = Field(None, max_length=50)
    nombre: str = Field(..., min_length=1, max_length=200)
    descripcion: str | None = Field(None, max_length=500)
    tipo_producto: str = "ARMAZON"
    unidad_medida: str = "PIEZA"
    atributos_opticos: dict = Field(default_factory=dict)
    costo_estandar: Decimal = Field(default=Decimal("0"), ge=0)
    precio_venta: Decimal = Field(default=Decimal("0"), ge=0)
    metodo_costeo: str = "PEPS"
    stock_minimo: Decimal = Field(default=Decimal("0"), ge=0)
    requiere_receta: bool = False
    requiere_lote: bool = False
    requiere_serie: bool = False
    es_servicio: bool = False


class ProductoResponse(ProductoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    created_at: datetime


class InventarioEntradaRequest(BaseModel):
    sucursal_id: UUID
    producto_id: UUID
    cantidad: Decimal = Field(..., gt=0)
    costo_unitario: Decimal = Field(..., ge=0)
    origen: str = Field(default="COMPRA", max_length=80)
    referencia: str | None = Field(None, max_length=120)
    lote: str | None = None
    numero_serie: str | None = None
    fecha_caducidad: date | None = None


class InventarioSalidaRequest(BaseModel):
    sucursal_id: UUID
    producto_id: UUID
    cantidad: Decimal = Field(..., gt=0)
    origen: str = Field(default="VENTA", max_length=80)
    referencia: str | None = Field(None, max_length=120)


class KardexResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    sucursal_id: UUID
    producto_id: UUID
    tipo_movimiento: str
    origen: str
    referencia: str | None
    cantidad: Decimal
    costo_unitario: Decimal
    costo_total: Decimal
    saldo_cantidad: Decimal
    saldo_valor: Decimal
    created_at: datetime


class CuentaContableCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=40)
    nombre: str = Field(..., min_length=1, max_length=200)
    tipo: str = Field(..., max_length=30)
    naturaleza: str = Field(..., pattern="^(DEUDORA|ACREEDORA)$")
    padre_id: UUID | None = None
    acepta_movimientos: bool = True


class CuentaContableResponse(CuentaContableCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID


class LineaAsientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    cuenta_id: UUID
    descripcion: str | None
    debe: Decimal
    haber: Decimal


class AsientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    empresa_id: UUID
    fecha: date
    descripcion: str
    origen: str
    referencia: str | None
    moneda: str
    estado: str
    lineas: list[LineaAsientoResponse] = []


class InventarioAlertaResponse(BaseModel):
    producto_id: UUID
    sucursal_id: UUID
    sku: str
    nombre: str
    tipo_alerta: str
    severidad: str
    cantidad_actual: Decimal
    stock_minimo: Decimal
    punto_reorden: Decimal | None = None
    valor_total: Decimal
    mensaje: str


class PeriodoContableCreate(BaseModel):
    codigo: str = Field(..., min_length=1, max_length=20)
    nombre: str = Field(..., min_length=1, max_length=120)
    fecha_inicio: date
    fecha_fin: date


class PeriodoContableResponse(PeriodoContableCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    empresa_id: UUID
    estado: str
    created_at: datetime


class PeriodoContableEstadoRequest(BaseModel):
    estado: str = Field(..., pattern="^(ABIERTO|CERRADO)$")
