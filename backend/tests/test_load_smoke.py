from argparse import Namespace
from pathlib import Path

from scripts.load_smoke import LoadPlan, RequestResult, evaluate, load_plan, percentile, summarize


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
    assert summary.p50_latency_ms == 20.0
    assert summary.p99_latency_ms == 30.0
    assert summary.status_codes == {"200": 1, "204": 1, "500": 1}
    assert summary.errors == {"server error": 1}


def test_evaluate_reports_every_breached_slo():
    plan = LoadPlan(
        urls=["http://test/health"],
        max_failure_rate=0.01,
        max_p95_ms=100,
        max_p99_ms=200,
        min_requests_per_second=20,
    )
    summary = summarize(
        [
            RequestResult(status_code=200, latency_ms=250),
            RequestResult(status_code=500, latency_ms=300, error="HTTP 500"),
        ],
        duration_seconds=1,
    )
    failures = evaluate(summary, plan)
    assert len(failures) == 4


def test_load_plan_reads_json_and_allows_cli_override(tmp_path: Path):
    path = tmp_path / "slo.json"
    path.write_text('{"urls":["http://test/health"],"requests":100,"concurrency":5}')
    args = Namespace(
        urls=None,
        requests=20,
        concurrency=None,
        warmup_requests=None,
        timeout_seconds=None,
        max_failure_rate=None,
        max_p95_ms=None,
        max_p99_ms=None,
        min_requests_per_second=None,
    )
    plan = load_plan(path, args)
    assert plan.requests == 20
    assert plan.concurrency == 5
    assert plan.urls == ["http://test/health"]
