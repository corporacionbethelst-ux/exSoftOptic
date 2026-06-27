from pathlib import Path


def test_outbox_service_has_retention_and_recovery_methods():
    source = (Path(__file__).resolve().parents[1] / "app" / "services" / "outbox_service.py").read_text()

    assert "async def release_stale_processing" in source
    assert "status=self.STATUS_PENDING" in source
    assert "async def cleanup_published" in source
    assert "delete(OutboxEvent)" in source


def test_cleanup_operational_data_script_is_tenant_scoped():
    source = (Path(__file__).resolve().parents[1] / "scripts" / "cleanup_operational_data.py").read_text()

    assert "--empresa-id" in source
    assert "IdempotencyService(session).cleanup_expired" in source
    assert "release_stale_processing" in source
    assert "cleanup_published" in source
    assert "await session.commit()" in source
