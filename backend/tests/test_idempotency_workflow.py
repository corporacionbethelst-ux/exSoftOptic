import uuid

import pytest

from app.models.empresa import Empresa
from app.services.idempotency_service import IdempotencyService


@pytest.mark.asyncio
async def test_idempotency_replays_completed_response(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Idempotency Test SA", rfc="IDE260619AA1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = IdempotencyService(db_session)
    first = await service.start(
        empresa_id=empresa.id,
        scope="ventas.confirmar",
        key="idem-venta-1",
        request_payload={"venta_id": "V-1", "total": "100.00"},
    )
    assert first.replay is False

    await service.complete(record=first.record, response_status=200, response_body={"id": "V-1", "estado": "CONFIRMADA"})
    second = await service.start(
        empresa_id=empresa.id,
        scope="ventas.confirmar",
        key="idem-venta-1",
        request_payload={"venta_id": "V-1", "total": "100.00"},
    )

    assert second.replay is True
    assert second.record.response_status == 200
    assert second.record.response_body == {"id": "V-1", "estado": "CONFIRMADA"}


@pytest.mark.asyncio
async def test_idempotency_rejects_same_key_with_different_payload(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Idempotency Conflict SA", rfc="IDE260619BB1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = IdempotencyService(db_session)
    await service.start(
        empresa_id=empresa.id,
        scope="facturacion.emitir",
        key="idem-factura-1",
        request_payload={"venta_id": "V-1"},
    )

    with pytest.raises(ValueError, match="payload distinto"):
        await service.start(
            empresa_id=empresa.id,
            scope="facturacion.emitir",
            key="idem-factura-1",
            request_payload={"venta_id": "V-2"},
        )


@pytest.mark.asyncio
async def test_idempotency_blocks_concurrent_processing(db_session):
    empresa = Empresa(id=uuid.uuid4(), razon_social="Idempotency Lock SA", rfc="IDE260619CC1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add(empresa)
    await db_session.flush()

    service = IdempotencyService(db_session)
    await service.start(
        empresa_id=empresa.id,
        scope="compras.recibir",
        key="idem-compra-1",
        request_payload={"orden_id": "OC-1"},
        lock_seconds=120,
    )

    with pytest.raises(ValueError, match="aún en procesamiento"):
        await service.start(
            empresa_id=empresa.id,
            scope="compras.recibir",
            key="idem-compra-1",
            request_payload={"orden_id": "OC-1"},
            lock_seconds=120,
        )


@pytest.mark.asyncio
async def test_idempotency_cleanup_removes_only_expired_records_for_tenant(db_session):
    from datetime import datetime, timedelta, timezone

    empresa = Empresa(id=uuid.uuid4(), razon_social="Idempotency Cleanup SA", rfc="IDE260620AA1", regimen_fiscal="601", codigo_postal="06600")
    otra_empresa = Empresa(id=uuid.uuid4(), razon_social="Other Cleanup SA", rfc="IDE260620BB1", regimen_fiscal="601", codigo_postal="06600")
    db_session.add_all([empresa, otra_empresa])
    await db_session.flush()

    service = IdempotencyService(db_session)
    expired = await service.start(
        empresa_id=empresa.id,
        scope="ventas.confirmar",
        key="expired-key",
        request_payload={"venta_id": "V-EXP"},
        ttl_hours=1,
    )
    active = await service.start(
        empresa_id=empresa.id,
        scope="ventas.confirmar",
        key="active-key",
        request_payload={"venta_id": "V-ACT"},
        ttl_hours=24,
    )
    await service.complete(record=active.record, response_status=200, response_body={"ok": True})
    other_tenant = await service.start(
        empresa_id=otra_empresa.id,
        scope="ventas.confirmar",
        key="other-expired-key",
        request_payload={"venta_id": "V-OTHER"},
        ttl_hours=1,
    )

    expired.record.expires_at = datetime.now(timezone.utc) - timedelta(hours=2)
    other_tenant.record.expires_at = datetime.now(timezone.utc) - timedelta(hours=2)
    other_tenant.record.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
    await db_session.flush()

    deleted = await service.cleanup_expired(empresa_id=empresa.id, limit=10)

    assert deleted == 1
    remaining = await service.start(
        empresa_id=empresa.id,
        scope="ventas.confirmar",
        key="active-key",
        request_payload={"venta_id": "V-ACT"},
    )
    assert remaining.record.id == active.record.id

    other_replay = await IdempotencyService(db_session).start(
        empresa_id=otra_empresa.id,
        scope="ventas.confirmar",
        key="other-expired-key",
        request_payload={"venta_id": "V-OTHER"},
        lock_seconds=0,
    )
    assert other_replay.record.id == other_tenant.record.id
