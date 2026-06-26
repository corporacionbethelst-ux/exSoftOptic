import uuid

import pytest

from app.models.empresa import Empresa
from app.schemas.auditoria import AuditoriaEventoCreate
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_log_builds_verifiable_hash_chain(db_session):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Audit Test SA de CV",
        rfc="AUD260619AA1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    db_session.add(empresa)
    await db_session.flush()

    service = AuditService(db_session)
    first = await service.record_event(
        empresa_id=empresa.id,
        usuario_id=None,
        payload=AuditoriaEventoCreate(
            accion="PRODUCTO_CREAR",
            entidad="Producto",
            entidad_id="SKU-AUD-1",
            payload={"sku": "SKU-AUD-1", "nombre": "Armazón auditado"},
            descripcion="Alta de producto desde catálogo",
        ),
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    second = await service.record_event(
        empresa_id=empresa.id,
        usuario_id=None,
        payload=AuditoriaEventoCreate(
            accion="PRODUCTO_ACTUALIZAR",
            entidad="Producto",
            entidad_id="SKU-AUD-1",
            payload={"precio_venta": "1499.00"},
        ),
    )

    assert first.secuencia == 1
    assert first.previous_hash is None
    assert second.secuencia == 2
    assert second.previous_hash == first.event_hash
    assert await service.verify_chain(empresa_id=empresa.id) is True

    events = await service.list_events(empresa_id=empresa.id, limit=10)
    assert [event.secuencia for event in events] == [2, 1]


@pytest.mark.asyncio
async def test_audit_chain_verification_reports_first_tampered_event(db_session):
    empresa = Empresa(
        id=uuid.uuid4(),
        razon_social="Audit Tamper SA de CV",
        rfc="AUD260620BB1",
        regimen_fiscal="601",
        codigo_postal="06600",
    )
    db_session.add(empresa)
    await db_session.flush()

    service = AuditService(db_session)
    first = await service.record_event(
        empresa_id=empresa.id,
        usuario_id=None,
        payload=AuditoriaEventoCreate(
            accion="VENTA_CONFIRMAR",
            entidad="Venta",
            entidad_id="V-AUD-1",
            payload={"total": "2500.00"},
        ),
    )
    await service.record_event(
        empresa_id=empresa.id,
        usuario_id=None,
        payload=AuditoriaEventoCreate(
            accion="VENTA_FACTURAR",
            entidad="Factura",
            entidad_id="F-AUD-1",
            payload={"uuid": "original"},
        ),
    )

    first.payload = {"total": "1.00"}
    await db_session.flush()

    verification = await service.verify_chain_details(empresa_id=empresa.id)

    assert verification.valid is False
    assert verification.first_invalid_sequence == 1
    assert verification.reason == "event_hash no coincide con el contenido del evento"
    assert verification.total_events == 1
