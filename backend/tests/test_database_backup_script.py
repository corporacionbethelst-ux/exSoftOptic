from pathlib import Path

from scripts.manage_database_backup import build_backup_command, build_restore_command, default_backup_path


def test_build_backup_command_uses_custom_format_and_safe_flags(tmp_path):
    output = tmp_path / "backup.dump"
    command = build_backup_command(
        database_url="postgresql+asyncpg://user:pass@localhost:5432/db",
        output=output,
    )

    assert command.args[:4] == ["pg_dump", "--format=custom", "--no-owner", "--no-privileges"]
    assert "--file" in command.args
    assert str(output) in command.args
    assert command.args[-1] == "postgresql+asyncpg://user:pass@localhost:5432/db"


def test_build_restore_command_can_clean_before_restore(tmp_path):
    input_file = tmp_path / "backup.dump"
    command = build_restore_command(
        database_url="postgresql+asyncpg://user:pass@localhost:5432/db",
        input_file=input_file,
        clean=True,
    )

    assert command.args[:4] == ["pg_restore", "--no-owner", "--no-privileges", "--dbname"]
    assert "--clean" in command.args
    assert "--if-exists" in command.args
    assert command.args[-1] == str(input_file)


def test_default_backup_path_uses_dump_extension(tmp_path):
    backup_path = default_backup_path(Path(tmp_path))

    assert backup_path.parent == tmp_path
    assert backup_path.name.startswith("exsoftoptic-backend-")
    assert backup_path.suffix == ".dump"
