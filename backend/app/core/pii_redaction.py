from __future__ import annotations

import re


_REDACTIONS = (
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"), "Bearer [REDACTED]"),
    (
        re.compile(r"(?i)(password|secret|api[_-]?key|token)\s*[=:]\s*[^\s,;]+"),
        r"\1=[REDACTED]",
    ),
    (
        re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
        "[EMAIL_REDACTED]",
    ),
)


def redact_sensitive_text(value: str) -> str:
    for pattern, replacement in _REDACTIONS:
        value = pattern.sub(replacement, value)
    return value
