from pathlib import Path

from scripts.verify_migrations import build_plan


def test_migration_verifier_default_plan_checks_head_and_idempotency():
    labels = [command.label for command in build_plan(roundtrip=False)]
    args = [command.args for command in build_plan(roundtrip=False)]

    assert labels == [
        "ensure single migration head",
        "upgrade database to head",
        "verify current revision",
        "verify upgrade idempotency",
    ]
    assert ["upgrade", "head"] in args
    assert ["downgrade", "base"] not in args


def test_migration_verifier_roundtrip_plan_downgrades_only_when_requested():
    args = [command.args for command in build_plan(roundtrip=True)]

    assert ["downgrade", "base"] in args
    assert args.count(["upgrade", "head"]) == 2


def test_migration_verifier_script_is_wired_in_backend_scripts():
    script = Path(__file__).resolve().parents[1] / "scripts" / "verify_migrations.py"

    assert script.exists()
    assert "--roundtrip" in script.read_text(encoding="utf-8")
