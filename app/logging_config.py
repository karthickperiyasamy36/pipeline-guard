 
import json
import logging
from datetime import datetime, timezone


# Standard LogRecord fields should not be repeated as custom fields.
STANDARD_LOG_RECORD_FIELDS = set(
    logging.makeLogRecord({}).__dict__.keys()
)


class JsonFormatter(logging.Formatter):
    """Format log records as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(
                record.created, timezone.utc
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Include custom fields supplied through logging's extra argument.
        for key, value in record.__dict__.items():
            if (
                key not in STANDARD_LOG_RECORD_FIELDS
                and key not in log_entry
                and key not in {"message", "asctime"}
            ):
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_entry,
            ensure_ascii=False,
            default=str,
        )


def configure_logging(level: str = "INFO") -> None:
    """Configure application-wide JSON logging."""

    numeric_level = getattr(logging, level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported logging level: {level}")

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)
