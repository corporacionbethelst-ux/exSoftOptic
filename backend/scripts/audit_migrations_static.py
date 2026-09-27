#!/usr/bin/env python3
"""Statically audit Alembic migration revision files before database execution."""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
VERSIONS_DIR = BACKEND_ROOT / "alembic" / "versions"
DANGEROUS_UPGRADE_OPS = {"drop_table", "drop_column"}


@dataclass(frozen=True)
class MigrationRevision:
    path: Path
    revision: str | None
    down_revision: str | None
    has_upgrade: bool
    has_downgrade: bool
    upgrade_ops: tuple[str, ...]


@dataclass(frozen=True)
class MigrationFinding:
    code: str
    detail: str


def parse_migration(path: Path) -> MigrationRevision:
    tree = ast.parse(path.read_text(), filename=str(path))
    revision: str | None = None
    down_revision: str | None = None
    has_upgrade = False
    has_downgrade = False
    upgrade_ops: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "revision":
                revision = _string_or_none(node.value)
            elif node.target.id == "down_revision":
                down_revision = _string_or_none(node.value)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "revision":
                    revision = _string_or_none(node.value)
                elif isinstance(target, ast.Name) and target.id == "down_revision":
                    down_revision = _string_or_none(node.value)
        elif isinstance(node, ast.FunctionDef) and node.name == "upgrade":
            has_upgrade = True
            upgrade_ops = _collect_op_calls(node)
        elif isinstance(node, ast.FunctionDef) and node.name == "downgrade":
            has_downgrade = True

    return MigrationRevision(path=path, revision=revision, down_revision=down_revision, has_upgrade=has_upgrade, has_downgrade=has_downgrade, upgrade_ops=tuple(upgrade_ops))


def _string_or_none(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    return None


def _collect_op_calls(function: ast.FunctionDef) -> list[str]:
    operations: list[str] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute):
            continue
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "op":
            operations.append(node.func.attr)
    return operations


def load_migrations(versions_dir: Path = VERSIONS_DIR) -> list[MigrationRevision]:
    return [parse_migration(path) for path in sorted(versions_dir.glob("*.py")) if path.name != "__init__.py"]


def audit_migrations_static(versions_dir: Path = VERSIONS_DIR) -> list[MigrationFinding]:
    findings: list[MigrationFinding] = []
    migrations = load_migrations(versions_dir)
    if not migrations:
        return [MigrationFinding("no-migrations", f"No migration files found in `{versions_dir}`.")]

    revisions: dict[str, MigrationRevision] = {}
    children_by_parent: dict[str | None, list[str]] = {}
    for migration in migrations:
        display = migration.path.name
        if not migration.revision:
            findings.append(MigrationFinding("missing-revision", f"Migration `{display}` has no revision identifier."))
            continue
        if migration.revision in revisions:
            findings.append(MigrationFinding("duplicate-revision", f"Revision `{migration.revision}` appears more than once."))
        revisions[migration.revision] = migration
        children_by_parent.setdefault(migration.down_revision, []).append(migration.revision)

        if migration.revision not in migration.path.name:
            findings.append(MigrationFinding("filename-revision-mismatch", f"Migration `{display}` does not include revision `{migration.revision}` in its filename."))
        if not migration.has_upgrade:
            findings.append(MigrationFinding("missing-upgrade", f"Migration `{display}` has no upgrade() function."))
        if not migration.has_downgrade:
            findings.append(MigrationFinding("missing-downgrade", f"Migration `{display}` has no downgrade() function."))
        for operation in migration.upgrade_ops:
            if operation in DANGEROUS_UPGRADE_OPS:
                findings.append(MigrationFinding("dangerous-upgrade-op", f"Migration `{display}` uses op.{operation}() in upgrade()."))

    roots = children_by_parent.get(None, [])
    if len(roots) != 1:
        findings.append(MigrationFinding("invalid-root-count", f"Expected exactly one root migration, found {len(roots)}."))

    for migration in migrations:
        if migration.down_revision is not None and migration.down_revision not in revisions:
            findings.append(MigrationFinding("unknown-down-revision", f"Migration `{migration.path.name}` points to unknown down_revision `{migration.down_revision}`."))

    heads = sorted(revision for revision in revisions if revision not in children_by_parent)
    if len(heads) != 1:
        findings.append(MigrationFinding("invalid-head-count", f"Expected exactly one migration head, found {len(heads)}: {heads}."))

    visited: set[str] = set()
    current = roots[0] if len(roots) == 1 else None
    while current is not None and current not in visited:
        visited.add(current)
        children = children_by_parent.get(current, [])
        if len(children) > 1:
            findings.append(MigrationFinding("branching-revision", f"Revision `{current}` has multiple children: {sorted(children)}."))
            break
        current = children[0] if children else None
    if len(visited) != len(revisions):
        missing = sorted(set(revisions) - visited)
        findings.append(MigrationFinding("disconnected-migration-graph", f"Migration graph is disconnected or cyclic; unreachable revisions: {missing}."))

    return findings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions-dir", type=Path, default=VERSIONS_DIR)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    findings = audit_migrations_static(args.versions_dir)
    if findings:
        for finding in findings:
            print(f"❌ {finding.code}: {finding.detail}")
        return 1
    print("✅ static migration audit passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
