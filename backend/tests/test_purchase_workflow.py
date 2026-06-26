from decimal import Decimal
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import AsientoContable, CuentaContable
from app.models.empresa import Empresa
from app.models.inventario import InventarioExistencia, KardexMovimiento
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.schemas.compras import OrdenCompraCreate, OrdenCompraLineaCreate, ProveedorCreate, RecepcionCompraCreate, RecepcionCompraLineaCreate
from app.services.purchase_service import PurchaseService


async def _base_compra(db_session: AsyncSession):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Compras Test SA", rfc="CTE260618AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="M1", nombre="Matriz")
    producto = Producto(id=uuid.uuid4(), empresa_id=empresa.id, sku="LENTE-COMPRA-001", nombre="Lente compra", precio_venta=Decimal("500"))
    cuentas = [
        CuentaContable(empresa_id=empresa.id, codigo="115.01", nombre="Inventario", tipo="ACTIVO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="201.01", nombre="Proveedores", tipo="PASIVO", naturaleza="ACREEDORA"),
    ]
    db_session.add_all([empresa, sucursal, producto, *cuentas])
    await db_session.flush()
    return empresa, sucursal, producto


def _orden_payload(sucursal_id, producto_id, folio="OC-100"):
    return OrdenCompraCreate(
        sucursal_id=sucursal_id,
        folio=folio,
        proveedor=ProveedorCreate(nombre="Proveedor Test", rfc="PTE260618AA1"),
        lineas=[OrdenCompraLineaCreate(producto_id=producto_id, cantidad=Decimal("10"), costo_unitario=Decimal("80"))],
    )


@pytest.mark.asyncio
async def test_recepcion_compra_alimenta_inventario_y_genera_cxp(db_session: AsyncSession):
    empresa, sucursal, producto = await _base_compra(db_session)
    service = PurchaseService(db_session)
    orden = await service.crear_orden(empresa_id=empresa.id, payload=_orden_payload(sucursal.id, producto.id))
    orden = await service.aprobar_orden(empresa_id=empresa.id, orden_id=orden.id)

    recepcion = await service.recibir_orden(
        empresa_id=empresa.id,
        orden_id=orden.id,
        payload=RecepcionCompraCreate(
            folio="RC-100",
            lineas=[RecepcionCompraLineaCreate(orden_linea_id=orden.lineas[0].id, cantidad=Decimal("10"), lote="L-1")],
        ),
    )

    assert recepcion.total == Decimal("800")
    assert recepcion.asiento_id is not None
    orden_recibida = await service.obtener_orden(empresa_id=empresa.id, orden_id=orden.id)
    assert orden_recibida.estado == "RECIBIDA"
    assert orden_recibida.lineas[0].cantidad_recibida == Decimal("10")

    existencia = await db_session.scalar(select(InventarioExistencia))
    assert existencia.cantidad == Decimal("10")
    assert existencia.valor_total == Decimal("800")

    kardex = await db_session.scalar(select(KardexMovimiento).where(KardexMovimiento.tipo_movimiento == "ENTRADA"))
    assert kardex.costo_total == Decimal("800")

    asiento = await db_session.get(AsientoContable, recepcion.asiento_id)
    assert asiento.origen == "COMPRA_RECIBIDA"


@pytest.mark.asyncio
async def test_recepcion_compra_rechaza_cantidad_mayor_a_pendiente(db_session: AsyncSession):
    empresa, sucursal, producto = await _base_compra(db_session)
    service = PurchaseService(db_session)
    orden = await service.crear_orden(empresa_id=empresa.id, payload=_orden_payload(sucursal.id, producto.id, folio="OC-101"))
    orden = await service.aprobar_orden(empresa_id=empresa.id, orden_id=orden.id)

    with pytest.raises(ValueError, match="cantidad recibida supera"):
        await service.recibir_orden(
            empresa_id=empresa.id,
            orden_id=orden.id,
            payload=RecepcionCompraCreate(
                folio="RC-101",
                lineas=[RecepcionCompraLineaCreate(orden_linea_id=orden.lineas[0].id, cantidad=Decimal("11"))],
            ),
        )
