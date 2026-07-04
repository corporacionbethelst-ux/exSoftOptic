from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import CuentaContable
from app.models.empresa import Empresa
from app.models.inventario import CapaInventario, InventarioExistencia
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.services.accounting_engine import AccountingEngine
from app.services.inventory_service import InventoryService


async def _empresa_sucursal_producto(db_session: AsyncSession):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Inventario Test SA",
        rfc="ITE260618AA1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    sucursal = Sucursal(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        codigo="MATRIZ",
        nombre="Matriz",
    )
    producto = Producto(
        id=uuid.uuid4(),
        empresa_id=empresa.id,
        sku="LENTE-PEPS-001",
        nombre="Lente PEPS",
        precio_venta=Decimal("250.00"),
    )
    db_session.add_all([empresa, sucursal, producto])
    await db_session.flush()
    return empresa, sucursal, producto


@pytest.mark.asyncio
async def test_salida_peps_valora_capas_en_orden_fifo(db_session: AsyncSession):
    empresa, sucursal, producto = await _empresa_sucursal_producto(db_session)
    service = InventoryService(db_session)

    await service.entrada(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("10"),
        costo_unitario=Decimal("100"),
        origen="COMPRA",
        referencia="OC-1",
    )
    await service.entrada(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("5"),
        costo_unitario=Decimal("120"),
        origen="COMPRA",
        referencia="OC-2",
    )

    movimiento, costo_total = await service.salida_peps(
        empresa_id=empresa.id,
        sucursal_id=sucursal.id,
        producto_id=producto.id,
        cantidad=Decimal("12"),
        origen="VENTA",
        referencia="V-1",
    )

    assert costo_total == Decimal("1240")
    assert movimiento.costo_total == Decimal("-1240")
    assert movimiento.saldo_cantidad == Decimal("3")

    existencia = await db_session.scalar(select(InventarioExistencia))
    assert existencia.cantidad == Decimal("3")
    assert existencia.valor_total == Decimal("360")

    capas = (await db_session.execute(select(CapaInventario).order_by(CapaInventario.created_at, CapaInventario.id))).scalars().all()
    assert capas[0].cantidad_disponible == Decimal("0")
    assert capas[1].cantidad_disponible == Decimal("3")


@pytest.mark.asyncio
async def test_salida_peps_rechaza_inventario_insuficiente(db_session: AsyncSession):
    empresa, sucursal, producto = await _empresa_sucursal_producto(db_session)

    with pytest.raises(ValueError, match="Inventario insuficiente"):
        await InventoryService(db_session).salida_peps(
            empresa_id=empresa.id,
            sucursal_id=sucursal.id,
            producto_id=producto.id,
            cantidad=Decimal("1"),
            origen="VENTA",
        )


@pytest.mark.asyncio
async def test_accounting_engine_crea_asiento_balanceado_de_venta(db_session: AsyncSession):
    empresa, _, _ = await _empresa_sucursal_producto(db_session)
    cuentas = [
        CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="401.01", nombre="Ventas", tipo="INGRESO", naturaleza="ACREEDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="501.01", nombre="Costo de venta", tipo="GASTO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="115.01", nombre="Inventario", tipo="ACTIVO", naturaleza="DEUDORA"),
    ]
    db_session.add_all(cuentas)
    await db_session.flush()

    asiento = await AccountingEngine(db_session).handle_venta_confirmada(
        empresa_id=empresa.id,
        fecha=date(2026, 6, 18),
        referencia="V-1",
        total=Decimal("1500"),
        costo=Decimal("900"),
    )

    assert len(asiento.lineas) == 4
    assert sum(linea.debe for linea in asiento.lineas) == Decimal("2400")
    assert sum(linea.haber for linea in asiento.lineas) == Decimal("2400")


@pytest.mark.asyncio
async def test_accounting_engine_rechaza_cuentas_inexistentes(db_session: AsyncSession):
    empresa, _, _ = await _empresa_sucursal_producto(db_session)

    with pytest.raises(ValueError, match="Cuentas contables inexistentes"):
        await AccountingEngine(db_session).handle_venta_confirmada(
            empresa_id=empresa.id,
            fecha=date(2026, 6, 18),
            referencia="V-2",
            total=Decimal("1500"),
            costo=Decimal("900"),
        )
