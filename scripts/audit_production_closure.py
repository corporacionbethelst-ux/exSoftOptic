#!/usr/bin/env python3
"""Audit the 15-phase roadmap and produce the production closure backlog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADING_RE = re.compile(r"^## (?:Cierre|Avance) de la fase (\d+)$", re.IGNORECASE)
CHECK_RE = re.compile(r"^- \[([ xX])\] (.+)$")


def parse_roadmap(text: str) -> dict[int, dict[str, list[str]]]:
    phases: dict[int, dict[str, list[str]]] = {}
    current: int | None = None
    for line in text.splitlines():
        heading = HEADING_RE.match(line.strip())
        if heading:
            current = int(heading.group(1))
            if current in phases:
                raise ValueError(f"duplicate roadmap section for phase {current}")
            phases[current] = {"completed": [], "pending": []}
            continue
        check = CHECK_RE.match(line.strip())
        if check and current is not None:
            bucket = "completed" if check.group(1).lower() == "x" else "pending"
            phases[current][bucket].append(check.group(2))
    expected = set(range(1, 16))
    if set(phases) != expected:
        missing = sorted(expected - set(phases))
        extra = sorted(set(phases) - expected)
        raise ValueError(f"roadmap phases invalid; missing={missing}, extra={extra}")
    for phase, checks in phases.items():
        if not checks["completed"] and not checks["pending"]:
            raise ValueError(f"phase {phase} has no exit criteria")
    return phases


def load_closure_plan(path: Path) -> dict[int, dict]:
    value = json.loads(path.read_text(encoding="utf-8"))
    entries = value.get("phases") if isinstance(value, dict) else None
    if not isinstance(entries, list):
        raise ValueError("closure plan phases must be a list")
    indexed: dict[int, dict] = {}
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("phase"), int):
            raise ValueError("each closure plan entry must contain an integer phase")
        phase = entry["phase"]
        if phase in indexed:
            raise ValueError(f"duplicate closure plan phase {phase}")
        if not str(entry.get("owner", "")).strip() or not str(entry.get("next_action", "")).strip():
            raise ValueError(f"phase {phase} requires owner and next_action")
        indexed[phase] = entry
    if set(indexed) != set(range(1, 16)):
        raise ValueError("closure plan must contain each phase from 1 through 15 exactly once")
    return indexed


def build_report(phases: dict[int, dict[str, list[str]]], plan: dict[int, dict]) -> dict:
    rows = []
    for phase in range(1, 16):
        completed = len(phases[phase]["completed"])
        pending = len(phases[phase]["pending"])
        rows.append({
            "phase": phase,
            "owner": plan[phase]["owner"],
            "next_action": plan[phase]["next_action"],
            "completed_criteria": completed,
            "pending_criteria": pending,
            "status": "closed" if pending == 0 else "open",
            "pending": phases[phase]["pending"],
        })
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_phases": 15,
        "closed_phases": sum(row["status"] == "closed" for row in rows),
        "open_phases": sum(row["status"] == "open" for row in rows),
        "pending_criteria": sum(row["pending_criteria"] for row in rows),
        "phases": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roadmap", default="docs/production-roadmap.md")
    parser.add_argument("--plan", default="ops/release/production-closure-plan.json")
    parser.add_argument("--output", default="artifacts/production-closure-report.json")
    parser.add_argument("--strict", action="store_true", help="Fail while any exit criterion remains pending")
    args = parser.parse_args()
    try:
        phases = parse_roadmap((ROOT / args.roadmap).read_text(encoding="utf-8"))
        plan = load_closure_plan(ROOT / args.plan)
        report = build_report(phases, plan)
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(
            f"Production closure: {report['closed_phases']}/15 phases closed; "
            f"{report['pending_criteria']} criteria pending. Report: {output}"
        )
        return 2 if args.strict and report["pending_criteria"] else 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"production closure audit failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
