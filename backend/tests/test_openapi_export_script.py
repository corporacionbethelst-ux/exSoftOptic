from pathlib import Path


def test_openapi_export_script_uses_fastapi_schema_generator():
    script = Path(__file__).resolve().parents[1] / "scripts" / "export_openapi.py"
    source = script.read_text()

    assert "from app.main import app" in source
    assert "app.openapi()" in source
    assert "../docs/openapi.json" in source
