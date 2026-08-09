#!/usr/bin/env python3
"""Evaluate a canary observation and emit an auditable rollout decision."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_RE = re.compile(r"^[0-9a-f]{7,64}$", re.IGNORECASE)


def load_json(path: Path) -> dict:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"invalid JSON number: {value}")),
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def metric_number(metrics: dict, name: str, *, maximum: float | None = None) -> float:
    if name not in metrics or isinstance(metrics[name], bool):
        raise ValueError(f"metric {name} is required and must be numeric")
    try:
        value = float(metrics[name])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"metric {name} must be numeric") from exc
    if not math.isfinite(value) or value < 0 or (maximum is not None and value > maximum):
        suffix = f" between 0 and {maximum}" if maximum is not None else " finite and non-negative"
        raise ValueError(f"metric {name} must be{suffix}")
    return value


def validate_policy(policy: dict) -> None:
    stages = policy.get("stages_percent")
    windows = policy.get("minimum_observation_minutes")
    thresholds = policy.get("thresholds")
    if policy.get("strategy") != "canary":
        raise ValueError("only the canary strategy is supported")
    if not isinstance(stages, list) or stages != sorted(set(stages or [])) or stages[-1:] != [100]:
        raise ValueError("stages_percent must be unique, increasing and end at 100")
    if not isinstance(windows, list) or len(windows) != len(stages):
        raise ValueError("each canary stage must define an observation window")
    required = {"maximum_error_rate", "maximum_p95_ms", "maximum_p99_ms", "minimum_health_success_rate"}
    if not isinstance(thresholds, dict) or required - thresholds.keys():
        raise ValueError("rollout thresholds are incomplete")


def evaluate(policy: dict, metrics: dict, current_stage: int) -> tuple[str, list[str], int]:
    stages = policy["stages_percent"]
    if current_stage not in stages:
        raise ValueError("current stage is not present in rollout policy")
    index = stages.index(current_stage)
    thresholds = policy["thresholds"]
    error_rate = metric_number(metrics, "error_rate", maximum=1.0)
    p95_ms = metric_number(metrics, "p95_ms")
    p99_ms = metric_number(metrics, "p99_ms")
    health_success_rate = metric_number(metrics, "health_success_rate", maximum=1.0)
    observation_minutes = metric_number(metrics, "observation_minutes")
    reasons: list[str] = []
    checks = (
        (error_rate > thresholds["maximum_error_rate"], "error_rate_threshold_breach"),
        (p95_ms > thresholds["maximum_p95_ms"], "p95_threshold_breach"),
        (p99_ms > thresholds["maximum_p99_ms"], "p99_threshold_breach"),
        (health_success_rate < thresholds["minimum_health_success_rate"], "health_check_failure"),
        (observation_minutes < policy["minimum_observation_minutes"][index], "observation_window_incomplete"),
    )
    reasons.extend(reason for failed, reason in checks if failed)
    if reasons:
        action = "rollback" if any(reason in policy["automatic_rollback_on"] for reason in reasons) else "hold"
        return action, reasons, current_stage
    if current_stage == 100:
        return "complete", ["all_thresholds_satisfied"], 100
    return "advance", ["all_thresholds_satisfied"], stages[index + 1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default="ops/release/production-rollout-policy.json")
    parser.add_argument("--metrics", required=True)
    parser.add_argument("--release-sha", required=True)
    parser.add_argument("--current-stage", type=int, required=True)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--change-ticket", required=True)
    parser.add_argument("--output", default="artifacts/production-rollout-decision.json")
    args = parser.parse_args()
    try:
        if not RELEASE_RE.fullmatch(args.release_sha):
            raise ValueError("release SHA must contain 7-64 hexadecimal characters")
        if len(args.approved_by.strip()) < 3 or len(args.change_ticket.strip()) < 3:
            raise ValueError("approver and change ticket are required")
        policy = load_json(ROOT / args.policy)
        validate_policy(policy)
        metrics = load_json(Path(args.metrics).resolve())
        action, reasons, next_stage = evaluate(policy, metrics, args.current_stage)
        decision = {
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
            "release_sha": args.release_sha.lower(),
            "current_stage_percent": args.current_stage,
            "next_stage_percent": next_stage,
            "action": action,
            "reasons": reasons,
            "approved_by": args.approved_by.strip(),
            "change_ticket": args.change_ticket.strip(),
            "metrics": metrics,
        }
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(decision, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(decision, sort_keys=True))
        return 2 if action == "rollback" else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"rollout evaluation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
