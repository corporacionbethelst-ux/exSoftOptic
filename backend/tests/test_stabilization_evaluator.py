import importlib.util
import math
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "evaluate_stabilization", ROOT / "scripts/evaluate_stabilization.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)
POLICY = MODULE.load_object(ROOT / "ops/release/stabilization-policy.json")
HEALTHY = {
    "days_observed": 14, "availability": 0.9999, "error_rate": 0.001,
    "p95_ms": 300, "sev1_incidents": 0, "sev2_incidents": 0,
    "open_critical_defects": 0, "completed_reviews": POLICY["required_reviews"],
}


def test_healthy_release_is_stabilized():
    assert MODULE.evaluate(POLICY, HEALTHY) == (
        "stabilized", ["all_stabilization_criteria_satisfied"]
    )


def test_short_observation_period_continues_monitoring():
    evidence = {**HEALTHY, "days_observed": 7}
    status, reasons = MODULE.evaluate(POLICY, evidence)
    assert status == "continue-observation"
    assert reasons == ["minimum_observation_period_incomplete"]


def test_slo_breach_requires_corrective_action():
    evidence = {**HEALTHY, "error_rate": 0.02, "sev1_incidents": 1}
    status, reasons = MODULE.evaluate(POLICY, evidence)
    assert status == "corrective-action"
    assert "error_rate_above_target" in reasons
    assert "sev1_incident_limit_exceeded" in reasons


def test_missing_review_blocks_stabilization():
    evidence = {**HEALTHY, "completed_reviews": ["slo-and-capacity"]}
    status, reasons = MODULE.evaluate(POLICY, evidence)
    assert status == "review-required"
    assert any(reason.startswith("missing_review:") for reason in reasons)


@pytest.mark.parametrize(
    ("field", "value"),
    [("availability", math.nan), ("error_rate", -0.1), ("p95_ms", "invalid"),
     ("sev1_incidents", -1), ("days_observed", True)],
)
def test_invalid_evidence_never_stabilizes(field, value):
    evidence = {**HEALTHY, field: value}
    with pytest.raises(ValueError, match=field):
        MODULE.evaluate(POLICY, evidence)


def test_completed_reviews_must_be_a_list():
    with pytest.raises(ValueError, match="completed_reviews"):
        MODULE.evaluate(POLICY, {**HEALTHY, "completed_reviews": "all"})
