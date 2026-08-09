from __future__ import annotations

import hmac


def metrics_token_is_valid(authorization: str | None, expected_token: str) -> bool:
    if not authorization or not expected_token:
        return False
    scheme, separator, supplied_token = authorization.partition(" ")
    return (
        bool(separator)
        and scheme.lower() == "bearer"
        and hmac.compare_digest(supplied_token, expected_token)
    )
