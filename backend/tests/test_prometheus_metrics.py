from app.core.metrics import RuntimeMetrics


def test_runtime_metrics_prometheus_text_includes_core_series():
    metrics = RuntimeMetrics()
    metrics.record_response(status_code=200, latency_ms=10.0, method="GET", path="/health")
    metrics.record_response(status_code=500, latency_ms=30.0)
    metrics.record_exception(latency_ms=5.0)

    prometheus = metrics.prometheus_text()

    assert "# TYPE exsoftoptic_requests_total counter" in prometheus
    assert "exsoftoptic_requests_total 3" in prometheus
    assert 'exsoftoptic_responses_total{status_code="200"} 1' in prometheus
    assert 'exsoftoptic_responses_total{status_code="500"} 1' in prometheus
    assert "exsoftoptic_exceptions_total 1" in prometheus
    assert "exsoftoptic_request_latency_average_ms 15.0" in prometheus
    assert 'exsoftoptic_route_responses_total{method="GET",path="/health",status_code="200"} 1' in prometheus
    assert "# TYPE exsoftoptic_request_latency_ms histogram" in prometheus
    assert 'exsoftoptic_request_latency_ms_bucket{le="10.0"} 1' in prometheus
    assert 'exsoftoptic_request_latency_ms_bucket{le="+Inf"} 3' in prometheus
    assert "exsoftoptic_request_latency_ms_count 3" in prometheus
    assert "exsoftoptic_requests_in_flight 0" in prometheus
