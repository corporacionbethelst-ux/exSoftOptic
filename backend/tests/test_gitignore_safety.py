from pathlib import Path


def test_gitignore_protects_local_test_environment_and_venvs():
    source = (Path(__file__).resolve().parents[2] / ".gitignore").read_text()

    assert "backend/.env.test.local" in source
    assert "backend/venv/" in source
    assert "__pycache__/" in source
    assert "!backend/.env.test.example" in source
