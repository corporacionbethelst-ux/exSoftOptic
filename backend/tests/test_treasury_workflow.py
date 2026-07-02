from datetime import date
from decimal import Decimal
import uuid

import pytest

from app.models.contabilidad import CuentaContable
from app.models.empresa import Empresa
from app.schemas.tesoreria import ConciliarMovimientoRequest, CuentaBancariaCreate, MovimientoBancarioCreate
from app.services.accounting_engine import AccountingEngine, AccountingLineInput
from app.services.treasury_service import TreasuryService


@pytest.mark.asyncio
async def test_tesoreria_concilia_movimiento_con_asiento_balanceado(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Treasury Test SA", rfc="TRE260619AA1", regimen_fiscal="601", codigo_postal="06600")
    bancos = CuentaContable(id=uuid.uuid4(), empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA")
    ingresos = CuentaContable(id=uuid.uuid4(), empresa_id=empresa.id, codigo="401.01", nombre="Ingresos", tipo="INGRESO", naturaleza="ACREEDORA")
    db_session.add_all([empresa, bancos, ingresos])
    await db_session.flush()

    asiento = await AccountingEngine(db_session).create_journal_entry(
        empresa_id=empresa.id,
        fecha=date(2026, 6, 19),
        descripcion="Cobro conciliable",
        origen="COBRO",
        referencia="DEP-1",
        lines=[
            AccountingLineInput("102.01", "Banco", debe=Decimal("1000")),
            AccountingLineInput("401.01", "Ingreso", haber=Decimal("1000")),
        ],
    )
    service = TreasuryService(db_session)
    cuenta = await service.crear_cuenta_bancaria(
        empresa_id=empresa.id,
        payload=CuentaBancariaCreate(cuenta_contable_id=bancos.id, banco="Banco Test", numero_cuenta="1234567890"),
    )
    movimiento = await service.registrar_movimiento(
        empresa_id=empresa.id,
        payload=MovimientoBancarioCreate(cuenta_bancaria_id=cuenta.id, fecha=date(2026, 6, 19), referencia="DEP-1", monto=Decimal("1000"), tipo="ABONO"),
    )

    conciliacion = await service.conciliar_movimiento(
        empresa_id=empresa.id,
        payload=ConciliarMovimientoRequest(movimiento_id=movimiento.id, asiento_id=asiento.id, observaciones="Match exacto"),
    )

    assert conciliacion.estado == "CONCILIADA"
    assert movimiento.estado == "CONCILIADO"
    assert movimiento.asiento_id == asiento.id
    assert movimiento.conciliado_en is not None
    assert await service.listar_movimientos_pendientes(empresa_id=empresa.id) == []
