"""Process-wide JSON logging; no third-party handlers or network dependencies."""

import json
import logging
import re
import traceback
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    # HTTP library exceptions may include Telegram tokens in URLs. Never render
    # exception messages, source lines, locals, URLs, headers or request bodies.
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "event": getattr(record, "event", "log"),
            "message": self._redact(record.getMessage()),
        }
        for field in (
            "actor_id",
            "target_id",
            "request_id",
            "job_id",
            "job_kind",
            "error_code",
            "status",
            "method",
            "route",
            "operation",
        ):
            value = getattr(record, field, None)
            if isinstance(value, (str, int, float, bool)):
                payload[field] = (
                    self._redact(value) if isinstance(value, str) else value
                )
        if record.exc_info and record.exc_info[1] is not None:
            payload["exception_type"] = type(record.exc_info[1]).__name__
            payload["stack"] = [
                {"file": frame.filename, "line": frame.lineno, "function": frame.name}
                for frame in traceback.extract_tb(record.exc_info[2])
            ]
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _redact(value: str) -> str:
        value = re.sub(r"\d{5,}:[A-Za-z0-9_-]{20,}", "[REDACTED]", value)
        value = re.sub(r"(?i)\bbearer\s+\S+", "Bearer [REDACTED]", value)
        return value


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler], force=True)
    for name in ("httpx", "httpcore", "urllib3"):
        logging.getLogger(name).setLevel(logging.WARNING)
