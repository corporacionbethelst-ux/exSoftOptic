from decimal import Decimal
import uuid

import pytest
from sqlalchemy import select

from app.models.contabilidad import CuentaContable
from app.models.empresa import Empresa
from app.models.inventario import InventarioExistencia, KardexMovimiento
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.schemas.ventas import ClienteCreate, DevolucionVentaCreate, DevolucionVentaLineaCreate, PagoVentaCreate, VentaCreate, VentaLineaCreate
from app.services.inventory_service import InventoryService
from app.services.sales_return_service import SalesReturnService
from app.services.sales_service import SalesService


async def _base(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Returns Test SA", rfc="RET260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="R1", nombre="Returns")
    producto = Producto(id=uuid.uuid4(), empresa_id=empresa.id, sku="RET-001", nombre="Armazón retorno", precio_venta=Decimal("500"))
    cuentas = [
        CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="401.01", nombre="Ventas", tipo="INGRESO", naturaleza="ACREEDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="501.01", nombre="Costo de venta", tipo="GASTO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="115.01", nombre="Inventario", tipo="ACTIVO", naturaleza="DEUDORA"),
    ]
    db_session.add_all([empresa, sucursal, producto, *cuentas])
    await db_session.flush()
    return empresa, sucursal, producto


def _venta_payload(sucursal_id, producto_id):
    return VentaCreate(
        sucursal_id=sucursal_id,
        folio="V-RET-1",
        cliente=ClienteCreate(nombre="Cliente Retorno", email="retorno@example.com"),
        lineas=[VentaLineaCreate(producto_id=producto_id, cantidad=Decimal("2"), precio_unitario=Decimal("500"))],
        pagos=[PagoVentaCreate(metodo_pago="EFECTIVO", monto=Decimal("1000"))],
    )


@pytest.mark.asyncio
async def test_devolucion_parcial_reingresa_inventario_y_genera_asiento(db_session):
    empresa, sucursal, producto = await _base(db_session)
    await InventoryService(db_session).entrada(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("5"),
        costo_unitario=Decimal("300"),
        origen="COMPRA",
        referencia="OC-RET-1",
    )
    venta_service = SalesService(db_session)
    venta = await venta_service.crear_venta(empresa_id=empresa.id, payload=_venta_payload(sucursal.id, producto.id))
    venta = await venta_service.confirmar_venta(empresa_id=empresa.id, venta_id=venta.id)

    devolucion = await SalesReturnService(db_session).registrar_devolucion(
        empresa_id=empresa.id,
        venta_id=venta.id,
        payload=DevolucionVentaCreate(
            folio="DV-1",
            motivo="Cambio de modelo",
            lineas=[DevolucionVentaLineaCreate(venta_linea_id=venta.lineas[0].id, cantidad=Decimal("1"))],
        ),
    )

    assert devolucion.total == Decimal("500.0000")
    assert devolucion.costo_total == Decimal("300.0000")
    assert devolucion.asiento_id is not None
    venta_actualizada = await venta_service.obtener_venta(empresa_id=empresa.id, venta_id=venta.id)
    assert venta_actualizada.estado == "PARCIALMENTE_DEVUELTA"

    existencia = await db_session.scalar(select(InventarioExistencia))
    assert existencia.cantidad == Decimal("4.000")
    entrada_devolucion = await db_session.scalar(select(KardexMovimiento).where(KardexMovimiento.origen == "DEVOLUCION_VENTA"))
    assert entrada_devolucion.costo_total == Decimal("300.0000")
