from datetime import date
from decimal import Decimal
import uuid

import pytest

from app.models.contabilidad import CuentaContable
from app.models.empresa import Empresa
from app.schemas.inventory_accounting import PeriodoContableCreate
from app.services.accounting_engine import AccountingEngine, AccountingLineInput
from app.services.accounting_period_service import AccountingPeriodService


@pytest.mark.asyncio
async def test_periodo_contable_bloquea_asiento_en_periodo_cerrado(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Period Test SA", rfc="PER260620AA1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()
    db_session.add_all(
        [
            CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
            CuentaContable(empresa_id=empresa.id, codigo="401.01", nombre="Ingresos", tipo="INGRESO", naturaleza="ACREEDORA"),
        ]
    )
    await db_session.flush()

    period_service = AccountingPeriodService(db_session)
    periodo = await period_service.crear_periodo(
        empresa_id=empresa.id,
        payload=PeriodoContableCreate(
            codigo="2026-06",
            nombre="Junio 2026",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 30),
        ),
    )
    await period_service.cambiar_estado(empresa_id=empresa.id, periodo_id=periodo.id, estado="CERRADO")

    with pytest.raises(ValueError, match="está cerrado"):
        await AccountingEngine(db_session).create_journal_entry(
            empresa_id=empresa.id,
            fecha=date(2026, 6, 20),
            descripcion="Venta en periodo cerrado",
            origen="TEST",
            referencia="T-1",
            lines=[
                AccountingLineInput("102.01", "Cargo", debe=Decimal("100")),
                AccountingLineInput("401.01", "Abono", haber=Decimal("100")),
            ],
        )


@pytest.mark.asyncio
async def test_periodo_contable_rechaza_solapamientos(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Period Overlap SA", rfc="PER260620BB1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = AccountingPeriodService(db_session)
    await service.crear_periodo(
        empresa_id=empresa.id,
        payload=PeriodoContableCreate(codigo="2026-Q2", nombre="Q2 2026", fecha_inicio=date(2026, 4, 1), fecha_fin=date(2026, 6, 30)),
    )

    with pytest.raises(ValueError, match="solapa"):
        await service.crear_periodo(
            empresa_id=empresa.id,
            payload=PeriodoContableCreate(codigo="2026-06", nombre="Junio 2026", fecha_inicio=date(2026, 6, 1), fecha_fin=date(2026, 6, 30)),
        )
