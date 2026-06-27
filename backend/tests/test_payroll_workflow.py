from datetime import date
from decimal import Decimal
import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contabilidad import AsientoContable, CuentaContable
from app.models.empresa import Empresa
from app.models.sucursal import Sucursal
from app.schemas.nomina import EmpleadoCreate, NominaConfirmarRequest, NominaPeriodoCreate
from app.services.payroll_service import PayrollService


async def _base_nomina(db_session: AsyncSession):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Nomina Test SA", rfc="NOM260619AA1", regimen_fiscal="601", codigo_postal="06600")
    sucursal = Sucursal(id=uuid.uuid4(), empresa_id=empresa.id, codigo="N1", nombre="Nómina")
    cuentas = [
        CuentaContable(empresa_id=empresa.id, codigo="601.01", nombre="Sueldos", tipo="GASTO", naturaleza="DEUDORA"),
        CuentaContable(empresa_id=empresa.id, codigo="102.01", nombre="Bancos", tipo="ACTIVO", naturaleza="DEUDORA"),
    ]
    db_session.add_all([empresa, sucursal, *cuentas])
    await db_session.flush()
    return empresa, sucursal


@pytest.mark.asyncio
async def test_calcular_nomina_genera_recibos_y_totales(db_session: AsyncSession):
    empresa, sucursal = await _base_nomina(db_session)
    service = PayrollService(db_session)
    await service.crear_empleado(
        empresa_id=empresa.id,
        payload=EmpleadoCreate(
            sucursal_id=sucursal.id,
            numero_empleado="E-1",
            nombre="Empleado Uno",
            fecha_ingreso=date(2026, 1, 1),
            salario_diario=Decimal("100"),
        ),
    )
    periodo = await service.crear_periodo(
        empresa_id=empresa.id,
        payload=NominaPeriodoCreate(folio="NOM-100", fecha_inicio=date(2026, 6, 1), fecha_fin=date(2026, 6, 7)),
    )

    periodo = await service.calcular_periodo(empresa_id=empresa.id, periodo_id=periodo.id)

    assert periodo.estado == "CALCULADO"
    assert periodo.total_percepciones == Decimal("700")
    assert periodo.total_neto == Decimal("700")
    assert len(periodo.recibos) == 1


@pytest.mark.asyncio
async def test_confirmar_nomina_genera_asiento_contable(db_session: AsyncSession):
    empresa, sucursal = await _base_nomina(db_session)
    service = PayrollService(db_session)
    await service.crear_empleado(
        empresa_id=empresa.id,
        payload=EmpleadoCreate(
            sucursal_id=sucursal.id,
            numero_empleado="E-2",
            nombre="Empleado Dos",
            fecha_ingreso=date(2026, 1, 1),
            salario_diario=Decimal("200"),
        ),
    )
    periodo = await service.crear_periodo(
        empresa_id=empresa.id,
        payload=NominaPeriodoCreate(folio="NOM-101", fecha_inicio=date(2026, 6, 1), fecha_fin=date(2026, 6, 7)),
    )
    periodo = await service.calcular_periodo(empresa_id=empresa.id, periodo_id=periodo.id)

    periodo = await service.confirmar_periodo(
        empresa_id=empresa.id,
        periodo_id=periodo.id,
        payload=NominaConfirmarRequest(),
    )

    assert periodo.estado == "CONFIRMADO"
    assert periodo.asiento_id is not None
    asiento = await db_session.get(AsientoContable, periodo.asiento_id)
    assert asiento.origen == "NOMINA_GENERADA"
