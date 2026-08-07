from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from app.core.request_context import get_request_context


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per line for log aggregation platforms."""

    def format(self, record: logging.LogRecord) -> str:
        context = get_request_context()
        payload: dict[str, object] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if context:
            payload["correlation_id"] = context.correlation_id
        for key in ("method", "path", "status_code", "duration_ms", "client_ip"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def configure_logging(*, level: str, log_format: str) -> None:
    handler = logging.StreamHandler()
    if log_format.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
