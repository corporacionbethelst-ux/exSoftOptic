import json
import logging

from app.core.logging_config import JsonFormatter
from app.core.observability_auth import metrics_token_is_valid
from app.core.pii_redaction import redact_sensitive_text
from app.core.request_context import safe_correlation_id


def test_metrics_token_requires_exact_bearer_secret() -> None:
    secret = "metrics-secret-with-at-least-thirty-two-characters"
    assert metrics_token_is_valid(f"Bearer {secret}", secret)
    assert metrics_token_is_valid(f"bearer {secret}", secret)
    assert not metrics_token_is_valid(secret, secret)
    assert not metrics_token_is_valid("Bearer wrong", secret)
    assert not metrics_token_is_valid(None, secret)


def test_correlation_id_rejects_header_injection_and_oversized_values() -> None:
    assert safe_correlation_id("client-request_123") == "client-request_123"
    generated = safe_correlation_id("unsafe\r\nX-Forged: true")
    assert "\r" not in generated and "\n" not in generated
    assert safe_correlation_id("x" * 129) != "x" * 129


def test_json_formatter_emits_machine_readable_request_fields() -> None:
    record = logging.LogRecord(
        name="exsoftoptic.http",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.method = "GET"
    record.path = "/health"
    record.status_code = 200
    record.duration_ms = 12.5
    payload = json.loads(JsonFormatter().format(record))
    assert payload["message"] == "request_completed"
    assert payload["method"] == "GET"
    assert payload["path"] == "/health"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 12.5


def test_log_redaction_removes_tokens_passwords_and_email_addresses() -> None:
    redacted = redact_sensitive_text(
        "Bearer abc.def token=secret-value password:unsafe user@example.com"
    )
    assert "abc.def" not in redacted
    assert "secret-value" not in redacted
    assert "unsafe" not in redacted
    assert "user@example.com" not in redacted
    assert redacted.count("[REDACTED]") == 3
    assert "[EMAIL_REDACTED]" in redacted
