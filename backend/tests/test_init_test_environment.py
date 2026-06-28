from pathlib import Path

from scripts.init_test_environment import init_env_file


def test_init_env_file_copies_template_without_overwriting(tmp_path: Path):
    template = tmp_path / "template.env"
    output = tmp_path / ".env.test.local"
    template.write_text("ENVIRONMENT=test\n")

    assert "wrote" in init_env_file(template=template, output=output)
    output.write_text("CUSTOM=true\n")

    assert "kept existing" in init_env_file(template=template, output=output)
    assert output.read_text() == "CUSTOM=true\n"


def test_init_env_file_force_overwrites_when_requested(tmp_path: Path):
    template = tmp_path / "template.env"
    output = tmp_path / ".env.test.local"
    template.write_text("ENVIRONMENT=test\n")
    output.write_text("CUSTOM=true\n")

    assert "wrote" in init_env_file(template=template, output=output, force=True)
    assert output.read_text() == "ENVIRONMENT=test\n"
