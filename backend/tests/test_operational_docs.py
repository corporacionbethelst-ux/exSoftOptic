from pathlib import Path


def test_backend_operational_runbook_documents_required_operations():
    runbook = Path(__file__).resolve().parents[2] / "docs" / "backend-operational-runbook.md"
    content = runbook.read_text()

    required_sections = [
        "Required environment",
        "Local verification",
        "Migration workflow",
        "Outbox operations",
        "Production integrations",
        "Release checklist",
    ]
    for section in required_sections:
        assert section in content


def test_env_example_includes_production_integration_settings():
    env_example = Path(__file__).resolve().parents[1] / ".env.example"
    content = env_example.read_text()

    required_keys = [
        "CFDI_PROVIDER=",
        "CFDI_TIMEOUT_SECONDS=",
        "BANKING_PROVIDER=",
        "BANKING_API_URL=",
        "BANKING_API_KEY=",
        "BANKING_TIMEOUT_SECONDS=",
    ]
    for key in required_keys:
        assert key in content
