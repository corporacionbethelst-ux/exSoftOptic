from scripts.load_smoke import RequestResult, percentile, summarize


def test_percentile_returns_nearest_rank_value():
    assert percentile([10.0, 20.0, 30.0, 40.0], 95) == 40.0
    assert percentile([10.0, 20.0, 30.0, 40.0], 50) == 20.0


def test_summarize_counts_success_and_failures():
    summary = summarize(
        [
            RequestResult(status_code=200, latency_ms=10.0),
            RequestResult(status_code=204, latency_ms=20.0),
            RequestResult(status_code=500, latency_ms=30.0, error="server error"),
        ]
    )

    assert summary.total == 3
    assert summary.success == 2
    assert summary.failed == 1
    assert summary.average_latency_ms == 20.0
    assert summary.p95_latency_ms == 30.0
