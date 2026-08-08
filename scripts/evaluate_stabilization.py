#!/usr/bin/env python3
"""Evaluate post-launch evidence and write a stabilization decision record."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"^[0-9a-f]{7,64}$", re.IGNORECASE)


def load_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
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
    breaches: list[str] = []
    checks = (
        (float(evidence.get("availability", 0.0)) < t["minimum_availability"], "availability_below_target"),
        (float(evidence.get("error_rate", 1.0)) > t["maximum_error_rate"], "error_rate_above_target"),
        (float(evidence.get("p95_ms", float("inf"))) > t["maximum_p95_ms"], "p95_above_target"),
        (int(evidence.get("sev1_incidents", 0)) > t["maximum_sev1_incidents"], "sev1_incident_limit_exceeded"),
        (int(evidence.get("sev2_incidents", 0)) > t["maximum_sev2_incidents"], "sev2_incident_limit_exceeded"),
        (int(evidence.get("open_critical_defects", 0)) > t["maximum_open_critical_defects"], "critical_defects_open"),
    )
    breaches.extend(reason for failed, reason in checks if failed)
    completed_reviews = set(evidence.get("completed_reviews", []))
    missing_reviews = sorted(set(policy["required_reviews"]) - completed_reviews)
    if breaches:
        return "corrective-action", breaches
    if int(evidence.get("days_observed", 0)) < policy["minimum_observation_days"]:
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
