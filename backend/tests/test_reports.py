from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import AsientoContable, CuentaContable, LineaAsientoContable
from app.models.empresa import Empresa
from app.models.inventario import InventarioExistencia
from app.models.producto import Producto
from app.models.sucursal import Sucursal
from app.models.venta import Cliente, Venta
from app.services.report_service import ReportService


async def _base_reportes(db_session: AsyncSession):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Reportes Test SA", rfc="REP260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="R1", nombre="Reportes")
    producto = Producto(id=uuid.uuid4(), empresa_id=empresa.id, sku="REP-001", nombre="Producto reporte", precio_venta=Decimal("100"))
    cliente = Cliente(id=uuid.uuid4(), empresa_id=empresa.id, nombre="Cliente Reporte")
    banco = CuentaContable(id=uuid.uuid4(), empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA")
    ingreso = CuentaContable(id=uuid.uuid4(), empresa_id=empresa.id, codigo="401.01", nombre="Ventas", tipo="INGRESO", naturaleza="ACREEDORA")
    asiento = AsientoContable(id=uuid.uuid4(), empresa_id=empresa.id, fecha=date(2026, 6, 19), descripcion="Venta", origen="TEST")
    lineas = [
        LineaAsientoContable(asiento_id=asiento.id, cuenta_id=banco.id, debe=Decimal("1000"), haber=Decimal("0")),
        LineaAsientoContable(asiento_id=asiento.id, cuenta_id=ingreso.id, debe=Decimal("0"), haber=Decimal("1000")),
    ]
    existencia = InventarioExistencia(empresa_id=empresa.id, sucursal_id=sucursal.id, producto_id=producto.id, cantidad=Decimal("5"), costo_promedio=Decimal("40"), valor_total=Decimal("200"))
    venta = Venta(id=uuid.uuid4(), empresa_id=empresa.id, sucursal_id=sucursal.id, cliente_id=cliente.id, folio="V-REP-1", estado="CONFIRMADA", subtotal=Decimal("1000"), impuestos=Decimal("0"), total=Decimal("1000"), costo_total=Decimal("600"))
    db_session.add_all([empresa, sucursal, producto, cliente, banco, ingreso, asiento, *lineas, existencia, venta])
    await db_session.flush()
    return empresa, sucursal


@pytest.mark.asyncio
async def test_balanza_comprobacion_reporta_debe_haber_balanceados(db_session: AsyncSession):
    empresa, _ = await _base_reportes(db_session)
    reporte = await ReportService(db_session).balanza_comprobacion(empresa_id=empresa.id)
    assert reporte.total_debe == Decimal("1000")
    assert reporte.total_haber == Decimal("1000")
    assert len(reporte.cuentas) == 2


@pytest.mark.asyncio
async def test_inventario_valuado_reporta_valor_total(db_session: AsyncSession):
    empresa, sucursal = await _base_reportes(db_session)
    reporte = await ReportService(db_session).inventario_valuado(empresa_id=empresa.id, sucursal_id=sucursal.id)
    assert reporte.total_valor == Decimal("200")
    assert reporte.items[0].cantidad == Decimal("5")


@pytest.mark.asyncio
async def test_margen_ventas_reporta_margen_real(db_session: AsyncSession):
    empresa, _ = await _base_reportes(db_session)
    reporte = await ReportService(db_session).margen_ventas(empresa_id=empresa.id)
    assert reporte.total_ventas == Decimal("1000")
    assert reporte.total_costo == Decimal("600")
    assert reporte.margen_total == Decimal("400")
