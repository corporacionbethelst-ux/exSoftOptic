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


@pytest.mark.asyncio
async def test_libro_diario_y_mayor_contable(db_session):
    from datetime import date
    from decimal import Decimal
    import uuid

    from app.models.contabilidad import CuentaContable
    from app.models.empresa import Empresa
    from app.services.accounting_engine import AccountingEngine, AccountingLineInput
    from app.services.report_service import ReportService

    empresa = Empresa(id=uuid.uuid4(), razon_social="Reportes Contables SA", rfc="REP260620AA1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()
    db_session.add_all(
        [
            CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="401.01", nombre="Ingresos", tipo="INGRESO", naturaleza="ACREEDORA"),
        ]
    )
    await db_session.flush()
    await AccountingEngine(db_session).create_journal_entry(
        empresa_id=empresa.id,
        fecha=date(2026, 6, 20),
        descripcion="Venta reporte",
        origen="TEST",
        referencia="R-1",
        lines=[
            AccountingLineInput("102.01", "Cargo banco", debe=Decimal("250")),
            AccountingLineInput("401.01", "Ingreso", haber=Decimal("250")),
        ],
    )

    service = ReportService(db_session)
    diario = await service.libro_diario(empresa_id=empresa.id, fecha_inicio=date(2026, 6, 1), fecha_fin=date(2026, 6, 30))
    mayor = await service.libro_mayor(empresa_id=empresa.id, cuenta_codigo="102.01")

    assert diario.total_debe == Decimal("250")
    assert diario.total_haber == Decimal("250")
    assert len(diario.lineas) == 2
    assert mayor.cuentas[0].codigo == "102.01"
    assert mayor.cuentas[0].saldo_final == Decimal("250")


@pytest.mark.asyncio
async def test_estados_financieros_calculan_resultados_y_balance(db_session):
    from datetime import date
    from decimal import Decimal
    import uuid

    from app.models.contabilidad import CuentaContable
    from app.models.empresa import Empresa
    from app.services.accounting_engine import AccountingEngine, AccountingLineInput
    from app.services.report_service import ReportService

    empresa = Empresa(id=uuid.uuid4(), razon_social="Estados Financieros SA", rfc="EFI260620AA1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()
    db_session.add_all(
        [
            CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="201.01", nombre="CxP", tipo="PASIVO", naturaleza="ACREEDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="301.01", nombre="Capital", tipo="CAPITAL", naturaleza="ACREEDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="401.01", nombre="Ingresos", tipo="INGRESO", naturaleza="ACREEDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="501.01", nombre="Costo", tipo="COSTO", naturaleza="DEUDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="601.01", nombre="Gasto", tipo="GASTO", naturaleza="DEUDORA"),
        ]
    )
    await db_session.flush()
    engine = AccountingEngine(db_session)
    await engine.create_journal_entry(
        empresa_id=empresa.id,
        fecha=date(2026, 6, 20),
        descripcion="Venta con costo y gasto",
        origen="TEST",
        referencia="EF-1",
        lines=[
            AccountingLineInput("102.01", "Banco", debe=Decimal("1000")),
            AccountingLineInput("401.01", "Ingreso", haber=Decimal("1000")),
            AccountingLineInput("501.01", "Costo", debe=Decimal("400")),
            AccountingLineInput("201.01", "CxP", haber=Decimal("400")),
            AccountingLineInput("601.01", "Gasto", debe=Decimal("100")),
            AccountingLineInput("301.01", "Capital", haber=Decimal("100")),
        ],
    )

    service = ReportService(db_session)
    resultados = await service.estado_resultados(empresa_id=empresa.id, fecha_inicio=date(2026, 6, 1), fecha_fin=date(2026, 6, 30))
    balance = await service.balance_general(empresa_id=empresa.id, fecha_fin=date(2026, 6, 30))

    assert resultados.ingresos == Decimal("1000")
    assert resultados.costos == Decimal("400")
    assert resultados.gastos == Decimal("100")
    assert resultados.utilidad_operativa == Decimal("500")
    assert balance.activos == Decimal("1000")
    assert balance.pasivos == Decimal("400")
    assert balance.capital == Decimal("100")
    assert balance.comprobacion == Decimal("500")
