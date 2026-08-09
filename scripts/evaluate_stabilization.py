#!/usr/bin/env python3
"""Evaluate post-launch evidence and write a stabilization decision record."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"^[0-9a-f]{7,64}$", re.IGNORECASE)


def load_object(path: Path) -> dict:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON number: {value}")),
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def evidence_number(evidence: dict, name: str, *, maximum: float | None = None) -> float:
    if name not in evidence or isinstance(evidence[name], bool):
        raise ValueError(f"evidence {name} is required and must be numeric")
    try:
        value = float(evidence[name])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"evidence {name} must be numeric") from exc
    if not math.isfinite(value) or value < 0 or (maximum is not None and value > maximum):
        suffix = f" between 0 and {maximum}" if maximum is not None else " finite and non-negative"
        raise ValueError(f"evidence {name} must be{suffix}")
    return value


def evidence_count(evidence: dict, name: str) -> int:
    value = evidence.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"evidence {name} must be a non-negative integer")
    return value


def validate_policy(policy: dict) -> None:
    thresholds = policy.get("thresholds")
    required = {
        "minimum_availability", "maximum_error_rate", "maximum_p95_ms",
        "maximum_sev1_incidents", "maximum_sev2_incidents", "maximum_open_critical_defects",
    }
    checkpoints = policy.get("checkpoints_days")
    minimum_days = policy.get("minimum_observation_days")
    if not isinstance(minimum_days, int) or minimum_days < 1:
        raise ValueError("minimum_observation_days must be a positive integer")
    if not isinstance(checkpoints, list) or checkpoints != sorted(set(checkpoints or [])):
        raise ValueError("checkpoints_days must be unique and increasing")
    if not checkpoints or checkpoints[-1] != minimum_days:
        raise ValueError("the final checkpoint must equal minimum_observation_days")
    if not isinstance(thresholds, dict) or required - thresholds.keys():
        raise ValueError("stabilization thresholds are incomplete")
    if not policy.get("required_reviews"):
        raise ValueError("required_reviews must not be empty")


def evaluate(policy: dict, evidence: dict) -> tuple[str, list[str]]:
    t = policy["thresholds"]
    availability = evidence_number(evidence, "availability", maximum=1.0)
    error_rate = evidence_number(evidence, "error_rate", maximum=1.0)
    p95_ms = evidence_number(evidence, "p95_ms")
    sev1_incidents = evidence_count(evidence, "sev1_incidents")
    sev2_incidents = evidence_count(evidence, "sev2_incidents")
    open_critical_defects = evidence_count(evidence, "open_critical_defects")
    days_observed = evidence_count(evidence, "days_observed")
    completed = evidence.get("completed_reviews")
    if not isinstance(completed, list) or any(not isinstance(item, str) for item in completed):
        raise ValueError("evidence completed_reviews must be a list of strings")
    breaches: list[str] = []
    checks = (
        (availability < t["minimum_availability"], "availability_below_target"),
        (error_rate > t["maximum_error_rate"], "error_rate_above_target"),
        (p95_ms > t["maximum_p95_ms"], "p95_above_target"),
        (sev1_incidents > t["maximum_sev1_incidents"], "sev1_incident_limit_exceeded"),
        (sev2_incidents > t["maximum_sev2_incidents"], "sev2_incident_limit_exceeded"),
        (open_critical_defects > t["maximum_open_critical_defects"], "critical_defects_open"),
    )
    breaches.extend(reason for failed, reason in checks if failed)
    completed_reviews = set(completed)
    missing_reviews = sorted(set(policy["required_reviews"]) - completed_reviews)
    if breaches:
        return "corrective-action", breaches
    if days_observed < policy["minimum_observation_days"]:
        return "continue-observation", ["minimum_observation_period_incomplete"]
    if missing_reviews:
        return "review-required", [f"missing_review:{name}" for name in missing_reviews]
    return "stabilized", ["all_stabilization_criteria_satisfied"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default="ops/release/stabilization-policy.json")
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--review-ticket", required=True)
    parser.add_argument("--output", default="artifacts/stabilization-decision.json")
    args = parser.parse_args()
    try:
        if not SHA_RE.fullmatch(args.release_sha):
            raise ValueError("release SHA must contain 7-64 hexadecimal characters")
        if len(args.owner.strip()) < 3 or len(args.review_ticket.strip()) < 3:
            raise ValueError("owner and review ticket are required")
        policy = load_object(ROOT / args.policy)
        validate_policy(policy)
        evidence = load_object(Path(args.evidence).resolve())
        status, reasons = evaluate(policy, evidence)
        record = {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "release_sha": args.release_sha.lower(),
            "status": status,
            "reasons": reasons,
            "owner": args.owner.strip(),
            "review_ticket": args.review_ticket.strip(),
            "evidence": evidence,
        }
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(record, sort_keys=True))
        return 2 if status == "corrective-action" else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"stabilization evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
