from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BalanzaCuentaResponse(BaseModel):
    cuenta_id: UUID
    codigo: str
    nombre: str
    tipo: str
    naturaleza: str
    debe: Decimal
    haber: Decimal
    saldo: Decimal


class BalanzaComprobacionResponse(BaseModel):
    empresa_id: UUID
    total_debe: Decimal
    total_haber: Decimal
    cuentas: list[BalanzaCuentaResponse]


class InventarioValuadoItemResponse(BaseModel):
    producto_id: UUID
    sucursal_id: UUID
    sku: str
    producto: str
    cantidad: Decimal
    costo_promedio: Decimal
    valor_total: Decimal


class InventarioValuadoResponse(BaseModel):
    empresa_id: UUID
    total_valor: Decimal
    items: list[InventarioValuadoItemResponse]


class MargenVentasItemResponse(BaseModel):
    venta_id: UUID
    folio: str
    total: Decimal
    costo_total: Decimal
    margen: Decimal
    margen_porcentaje: Decimal


class MargenVentasResponse(BaseModel):
    empresa_id: UUID
    total_ventas: Decimal
    total_costo: Decimal
    margen_total: Decimal
    margen_porcentaje: Decimal
    ventas: list[MargenVentasItemResponse]
