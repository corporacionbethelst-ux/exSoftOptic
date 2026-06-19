import uuid

import pytest

from app.models.empresa import Empresa
from app.schemas.outbox import OutboxEventCreate
from app.services.outbox_service import OutboxService


@pytest.mark.asyncio
async def test_outbox_enqueue_is_idempotent_and_lists_pending(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Outbox Test SA", rfc="OUT260619AA1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = OutboxService(db_session)
    payload = OutboxEventCreate(
        aggregate_type="Venta",
        aggregate_id="V-100",
        event_type="VentaConfirmada",
        payload={"total": "1500.00"},
        idempotency_key="venta-v-100-confirmada",
    )

    first = await service.enqueue(empresa_id=empresa.id, payload=payload)
    second = await service.enqueue(empresa_id=empresa.id, payload=payload)
    pending = await service.list_pending(empresa_id=empresa.id)

    assert first.id == second.id
    assert len(pending) == 1
    assert pending[0].status == OutboxService.STATUS_PENDING


@pytest.mark.asyncio
async def test_outbox_processing_failure_retry_and_publish(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Outbox Retry SA", rfc="OUT260619BB1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = OutboxService(db_session)
    event = await service.enqueue(
        empresa_id=empresa.id,
        payload=OutboxEventCreate(
            aggregate_type="Factura",
            aggregate_id="F-100",
            event_type="FacturaTimbrada",
            payload={"uuid": "abc"},
            max_attempts=2,
        ),
    )

    processing = await service.mark_processing(empresa_id=empresa.id, event_id=event.id)
    assert processing.status == OutboxService.STATUS_PROCESSING
    assert processing.attempts == 1

    failed_once = await service.mark_failed(empresa_id=empresa.id, event_id=event.id, error="broker unavailable", retry_delay_seconds=0)
    assert failed_once.status == OutboxService.STATUS_PENDING
    assert failed_once.last_error == "broker unavailable"

    processing_again = await service.mark_processing(empresa_id=empresa.id, event_id=event.id)
    published = await service.mark_published(empresa_id=empresa.id, event_id=processing_again.id)

    assert published.status == OutboxService.STATUS_PUBLISHED
    assert published.published_at is not None
    with pytest.raises(ValueError, match="no está disponible"):
        await service.mark_processing(empresa_id=empresa.id, event_id=event.id)
