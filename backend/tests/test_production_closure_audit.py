import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "audit_production_closure", ROOT / "scripts/audit_production_closure.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_repository_roadmap_and_closure_plan_cover_all_phases():
    phases = MODULE.parse_roadmap((ROOT / "docs/production-roadmap.md").read_text())
    plan = MODULE.load_closure_plan(ROOT / "ops/release/production-closure-plan.json")
    report = MODULE.build_report(phases, plan)
    assert report["total_phases"] == 15
    assert report["closed_phases"] + report["open_phases"] == 15
    assert report["pending_criteria"] > 0
    assert all(row["owner"] and row["next_action"] for row in report["phases"])


def test_parser_rejects_incomplete_roadmap():
    with pytest.raises(ValueError, match="missing"):
        MODULE.parse_roadmap("## Cierre de la fase 1\n- [x] listo\n")


def test_phase_is_closed_only_without_pending_criteria():
    phases = {
        phase: {"completed": ["done"], "pending": [] if phase == 1 else ["todo"]}
        for phase in range(1, 16)
    }
    plan = {phase: {"phase": phase, "owner": "owner", "next_action": "action"}
            for phase in range(1, 16)}
    report = MODULE.build_report(phases, plan)
    assert report["closed_phases"] == 1
    assert report["open_phases"] == 14
