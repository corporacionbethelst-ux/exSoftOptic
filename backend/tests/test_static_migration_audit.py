from pathlib import Path

from scripts.audit_migrations_static import MigrationFinding, audit_migrations_static, parse_migration


def _write_migration(path: Path, revision: str, down_revision: str | None, upgrade_body: str = "pass") -> None:
    down_value = "None" if down_revision is None else repr(down_revision)
    path.write_text(
        f"revision = {revision!r}\n"
        f"down_revision = {down_value}\n"
        "def upgrade():\n"
        f"    {upgrade_body}\n"
        "def downgrade():\n"
        "    pass\n"
    )


def test_static_migration_audit_passes_current_versions():
    assert audit_migrations_static() == []


def test_parse_migration_extracts_revision_and_upgrade_ops(tmp_path: Path):
    migration = tmp_path / "abc_initial.py"
    _write_migration(migration, "abc", None, "op.create_table('x')")

    parsed = parse_migration(migration)

    assert parsed.revision == "abc"
    assert parsed.down_revision is None
    assert parsed.has_upgrade is True
    assert parsed.has_downgrade is True
    assert parsed.upgrade_ops == ("create_table",)


def test_static_migration_audit_detects_multiple_heads(tmp_path: Path):
    _write_migration(tmp_path / "base.py", "base", None)
    _write_migration(tmp_path / "left.py", "left", "base")
    _write_migration(tmp_path / "right.py", "right", "base")

    findings = audit_migrations_static(tmp_path)

    assert any(finding.code == "invalid-head-count" for finding in findings)
    assert any(finding.code == "branching-revision" for finding in findings)


def test_static_migration_audit_blocks_destructive_upgrade_ops(tmp_path: Path):
    _write_migration(tmp_path / "base.py", "base", None, "op.drop_table('x')")

    findings = audit_migrations_static(tmp_path)

    assert MigrationFinding("dangerous-upgrade-op", "Migration `base.py` uses op.drop_table() in upgrade().") in findings
