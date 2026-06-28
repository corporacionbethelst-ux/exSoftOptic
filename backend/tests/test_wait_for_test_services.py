from scripts.wait_for_test_services import DEFAULT_PROBES, ServiceProbe, wait_for_services


def test_default_test_service_probes_match_isolated_ports():
    probes = {probe.name: probe for probe in DEFAULT_PROBES}

    assert probes["postgres-test"].port == 55432
    assert probes["redis-test"].port == 56379
    assert probes["mongodb-test"].port == 57017


def test_wait_for_services_reports_unreachable_probe_quickly():
    missing = wait_for_services(
        [ServiceProbe("closed-test-port", "127.0.0.1", 9)],
        timeout_seconds=0.01,
        interval_seconds=0.01,
    )

    assert missing == ["closed-test-port"]
