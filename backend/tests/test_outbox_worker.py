from app.workers.outbox_worker import OutboxWorkerConfig, default_outbox_handlers


def test_default_outbox_handlers_cover_emitted_domain_events():
    handlers = default_outbox_handlers()

    assert "VentaConfirmada" in handlers
    assert "CompraRecibida" in handlers
    assert "FacturaTimbrada" in handlers
    assert "FacturaCancelada" in handlers


def test_outbox_worker_config_defaults_are_operational():
    config = OutboxWorkerConfig()

    assert config.poll_interval_seconds == 5.0
    assert config.batch_size == 100
