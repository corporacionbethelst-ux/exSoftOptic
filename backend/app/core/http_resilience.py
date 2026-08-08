from __future__ import annotations

import httpx


TRANSIENT_HTTP_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}


def is_transient_http_error(error: BaseException) -> bool:
    if isinstance(error, (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout)):
        return True
    if isinstance(error, httpx.HTTPStatusError):
        return error.response.status_code in TRANSIENT_HTTP_STATUS_CODES
    return False
