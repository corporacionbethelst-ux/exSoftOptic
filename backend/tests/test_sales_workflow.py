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
from app.schemas.ventas import ClienteCreate, PagoVentaCreate, VentaCreate, VentaLineaCreate
from app.services.inventory_service import InventoryService
from app.services.sales_service import SalesService


async def _base_venta(db_session: AsyncSession):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Ventas Test SA",
        rfc="VTE260618AA1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="M1", nombre="Matriz")
    producto = Producto(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        sku="ARMAZON-VENTA-001",
        nombre="Armazón venta",
        precio_venta=Decimal("500"),
    )
    cuentas = [
        CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="401.01", nombre="Ventas", tipo="INGRESO", naturaleza="ACREEDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="501.01", nombre="Costo de venta", tipo="GASTO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="115.01", nombre="Inventario", tipo="ACTIVO", naturaleza="DEUDORA"),
    ]
    db_session.add_all([empresa, sucursal, producto, *cuentas])
    await db_session.flush()
    return empresa, sucursal, producto


def _payload(sucursal_id, producto_id, folio="V-100"):
    return VentaCreate(
        sucursal_id=sucursal_id,
        folio=folio,
        cliente=ClienteCreate(nombre="Cliente Venta", email="cliente.venta@example.com"),
        lineas=[
            VentaLineaCreate(
                producto_id=producto_id,
                cantidad=Decimal("2"),
                precio_unitario=Decimal("500"),
            )
        ],
        pagos=[PagoVentaCreate(metodo_pago="EFECTIVO", monto=Decimal("1000"))],
    )


@pytest.mark.asyncio
async def test_confirmar_venta_descuenta_inventario_y_genera_asiento(db_session: AsyncSession):
    empresa, sucursal, producto = await _base_venta(db_session)
    await InventoryService(db_session).entrada(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("5"),
        costo_unitario=Decimal("300"),
        origen="COMPRA",
        referencia="OC-VTA-1",
    )

    service = SalesService(db_session)
    venta = await service.crear_venta(empresa_id=empresa.id, payload=_payload(sucursal.id, producto.id))
    venta_confirmada = await service.confirmar_venta(empresa_id=empresa.id, venta_id=venta.id)

    assert venta_confirmada.estado == "CONFIRMADA"
    assert venta_confirmada.total == Decimal("1000")
    assert venta_confirmada.costo_total == Decimal("600")
    assert venta_confirmada.asiento_id is not None
    assert venta_confirmada.lineas[0].costo_total == Decimal("600")

    existencia = await db_session.scalar(select(InventarioExistencia))
    assert existencia.cantidad == Decimal("3")
    assert existencia.valor_total == Decimal("900")

    kardex_salida = await db_session.scalar(select(KardexMovimiento).where(KardexMovimiento.tipo_movimiento == "SALIDA"))
    assert kardex_salida.costo_total == Decimal("-600")

    asiento = await db_session.get(AsientoContable, venta_confirmada.asiento_id)
    assert asiento is not None
    assert asiento.origen == "VENTA_CONFIRMADA"


@pytest.mark.asyncio
async def test_confirmar_venta_rechaza_inventario_insuficiente(db_session: AsyncSession):
    empresa, sucursal, producto = await _base_venta(db_session)
    service = SalesService(db_session)
    venta = await service.crear_venta(empresa_id=empresa.id, payload=_payload(sucursal.id, producto.id, folio="V-101"))

    with pytest.raises(ValueError, match="Inventario insuficiente"):
        await service.confirmar_venta(empresa_id=empresa.id, venta_id=venta.id)

    venta_sin_confirmar = await service.obtener_venta(empresa_id=empresa.id, venta_id=venta.id)
    assert venta_sin_confirmar.estado == "BORRADOR"
    assert venta_sin_confirmar.asiento_id is None

@pytest.mark.asyncio
async def test_confirmar_venta_revierte_inventario_si_falla_contabilidad(db_session: AsyncSession):
    empresa, sucursal, producto = await _base_venta(db_session)
    # Eliminar cuentas para forzar falla contable después de consumir inventario dentro del savepoint.
    for cuenta in (await db_session.execute(select(CuentaContable))).scalars().all():
        await db_session.delete(cuenta)
    await db_session.flush()
    await InventoryService(db_session).entrada(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("5"),
        costo_unitario=Decimal("300"),
        origen="COMPRA",
        referencia="OC-VTA-ROLLBACK",
    )

    service = SalesService(db_session)
    venta = await service.crear_venta(empresa_id=empresa.id, payload=_payload(sucursal.id, producto.id, folio="V-102"))

    with pytest.raises(ValueError, match="Cuentas contables inexistentes"):
        await service.confirmar_venta(empresa_id=empresa.id, venta_id=venta.id)

    existencia = await db_session.scalar(select(InventarioExistencia))
    assert existencia.cantidad == Decimal("5")
    assert existencia.valor_total == Decimal("1500")

    salidas = (await db_session.execute(select(KardexMovimiento).where(KardexMovimiento.tipo_movimiento == "SALIDA"))).scalars().all()
    assert salidas == []
    venta_sin_confirmar = await service.obtener_venta(empresa_id=empresa.id, venta_id=venta.id)
    assert venta_sin_confirmar.estado == "BORRADOR"
    assert venta_sin_confirmar.asiento_id is None
