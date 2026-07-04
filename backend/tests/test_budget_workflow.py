from datetime import date
from decimal import Decimal
import uuid

import pytest

from app.models.empresa import Empresa
from app.schemas.presupuestos import CentroCostoCreate, ComprometerPresupuestoRequest, PresupuestoCreate, PresupuestoLineaCreate
from app.services.budget_service import BudgetService


@pytest.mark.asyncio
async def test_presupuesto_compromete_monto_y_bloquea_exceso(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Budget Test SA", rfc="BUD260619AA1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = BudgetService(db_session)
    centro = await service.crear_centro_costo(
        empresa_id=empresa.id,
        payload=CentroCostoCreate(codigo="LAB", nombre="Laboratorio"),
    )
    presupuesto = await service.crear_presupuesto(
        empresa_id=empresa.id,
        payload=PresupuestoCreate(
            centro_costo_id=centro.id,
            folio="P-1",
            nombre="Presupuesto laboratorio Q3",
            fecha_inicio=date(2026, 7, 1),
            fecha_fin=date(2026, 9, 30),
            lineas=[PresupuestoLineaCreate(cuenta_codigo="501.01", monto=Decimal("1000"))],
        ),
    )

    presupuesto = await service.comprometer(
        empresa_id=empresa.id,
        payload=ComprometerPresupuestoRequest(presupuesto_id=presupuesto.id, cuenta_codigo="501.01", monto=Decimal("400")),
    )

    assert presupuesto.estado == "APROBADO"
    assert presupuesto.lineas[0].monto_comprometido == Decimal("400")
    with pytest.raises(ValueError, match="Presupuesto insuficiente"):
        await service.comprometer(
            empresa_id=empresa.id,
            payload=ComprometerPresupuestoRequest(presupuesto_id=presupuesto.id, cuenta_codigo="501.01", monto=Decimal("700")),
        )
