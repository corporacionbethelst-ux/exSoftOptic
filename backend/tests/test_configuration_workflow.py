import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.models.empresa import Empresa
from app.schemas.configuracion import ImpuestoCreate, ReglaContableCreate, SerieFolioCreate, TipoCambioCreate
from app.services.configuration_service import ConfigurationService


@pytest.mark.asyncio
async def test_configuration_service_manages_tax_folio_exchange_and_accounting_rules(db_session):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Config Test SA de CV",
        rfc="CFG260619AA1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    db_session.add(empresa)
    await db_session.flush()

    service = ConfigurationService(db_session)
    impuesto = await service.crear_impuesto(
        empresa_id=empresa.id,
        payload=ImpuestoCreate(codigo="IVA16", nombre="IVA 16%", tipo="IVA", tasa=Decimal("0.160000")),
    )
    serie = await service.crear_serie(
        empresa_id=empresa.id,
        payload=SerieFolioCreate(documento="FACTURA", serie="A", formato="{serie}-{folio:04d}"),
    )
    tipo_cambio = await service.crear_tipo_cambio(
        empresa_id=empresa.id,
        payload=TipoCambioCreate(moneda_origen="usd", moneda_destino="mxn", fecha=date(2026, 6, 19), tasa=Decimal("18.50000000")),
    )
    regla = await service.crear_regla_contable(
        empresa_id=empresa.id,
        payload=ReglaContableCreate(
            evento="VENTA_CONFIRMADA",
            descripcion="Regla default de venta",
            cuentas={"ingresos": "4000", "bancos": "1020"},
        ),
    )

    assert impuesto.codigo == "IVA16"
    assert serie.folio_actual == 0
    assert tipo_cambio.moneda_origen == "USD"
    assert regla.cuentas["ingresos"] == "4000"
    assert await service.siguiente_folio(empresa_id=empresa.id, documento="FACTURA", serie="A") == "A-0001"
    assert await service.siguiente_folio(empresa_id=empresa.id, documento="FACTURA", serie="A") == "A-0002"
    assert (await service.obtener_tipo_cambio(empresa_id=empresa.id, moneda_origen="USD", moneda_destino="MXN")).tasa == Decimal("18.50000000")
    assert len(await service.listar_impuestos(empresa_id=empresa.id)) == 1
    assert len(await service.listar_reglas_contables(empresa_id=empresa.id)) == 1
