import importlib.util
from pathlib import Path


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
