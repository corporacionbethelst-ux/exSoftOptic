import importlib.util
from pathlib import Path

import pytest


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "staging_release_rehearsal.py"
SPEC = importlib.util.spec_from_file_location("staging_release_rehearsal", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_release_plan_has_migration_before_deployment():
    plan = MODULE.load_plan(Path(__file__).resolve().parents[2] / "ops/release/staging-plan.json")
    commands = MODULE.release_commands(plan, ".env.staging", "https://staging.example.com")
    rendered = [" ".join(command) for command in commands]
    migration = next(i for i, command in enumerate(rendered) if "migration-job" in command)
    deployment = next(i for i, command in enumerate(rendered) if " up -d " in f" {command} ")
    assert migration < deployment
    assert any("validate_runtime_config.py" in command for command in rendered)
    assert any("load_smoke.py" in command for command in rendered)
    assert any("browser_smoke.py" in command for command in rendered)


@pytest.mark.parametrize("tag", ["", "registry/app:latest", "registry/app:production"])
def test_mutable_image_references_are_rejected(tmp_path, tag):
    env_file = tmp_path / ".env"
    env_file.write_text(f"BACKEND_IMAGE={tag}\nFRONTEND_IMAGE=registry/ui:2026.08.08-abc1234\n")
    with pytest.raises(ValueError, match="BACKEND_IMAGE"):
        MODULE.check_image_references(env_file)


def test_versioned_image_references_are_accepted(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "BACKEND_IMAGE=registry/api:2026.08.08-abc1234\n"
        "FRONTEND_IMAGE=registry/ui:2026.08.08-abc1234\n"
    )
    MODULE.check_image_references(env_file)
