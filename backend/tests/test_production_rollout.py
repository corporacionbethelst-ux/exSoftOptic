import importlib.util
import math
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "evaluate_production_rollout.py"
SPEC = importlib.util.spec_from_file_location("evaluate_production_rollout", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)
POLICY = MODULE.load_json(Path(__file__).resolve().parents[2] / "ops/release/production-rollout-policy.json")


def test_healthy_canary_advances_to_next_stage():
    action, reasons, next_stage = MODULE.evaluate(
        POLICY,
        {"error_rate": 0.001, "p95_ms": 200, "p99_ms": 400,
         "health_success_rate": 1.0, "observation_minutes": 15},
        5,
    )
    assert (action, next_stage) == ("advance", 25)
    assert reasons == ["all_thresholds_satisfied"]


def test_error_threshold_breach_rolls_back():
    action, reasons, next_stage = MODULE.evaluate(
        POLICY,
        {"error_rate": 0.02, "p95_ms": 200, "p99_ms": 400,
         "health_success_rate": 1.0, "observation_minutes": 15},
        5,
    )
    assert action == "rollback"
    assert next_stage == 5
    assert "error_rate_threshold_breach" in reasons


def test_incomplete_observation_holds_current_stage():
    action, reasons, next_stage = MODULE.evaluate(
        POLICY,
        {"error_rate": 0.0, "p95_ms": 100, "p99_ms": 200,
         "health_success_rate": 1.0, "observation_minutes": 10},
        5,
    )
    assert (action, next_stage) == ("hold", 5)
    assert reasons == ["observation_window_incomplete"]


def test_healthy_full_rollout_completes():
    action, _, next_stage = MODULE.evaluate(
        POLICY,
        {"error_rate": 0.0, "p95_ms": 100, "p99_ms": 200,
         "health_success_rate": 1.0, "observation_minutes": 120},
        100,
    )
    assert (action, next_stage) == ("complete", 100)


@pytest.mark.parametrize(
    ("field", "value"),
    [("error_rate", math.nan), ("p95_ms", -1), ("health_success_rate", 1.1),
     ("observation_minutes", True)],
)
def test_invalid_metrics_never_promote(field, value):
    metrics = {"error_rate": 0.0, "p95_ms": 100, "p99_ms": 200,
               "health_success_rate": 1.0, "observation_minutes": 15}
    metrics[field] = value
    with pytest.raises(ValueError, match=field):
        MODULE.evaluate(POLICY, metrics, 5)
