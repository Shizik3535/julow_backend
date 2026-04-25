import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, WrappedLogger

from app.core.config import settings


class LogLevelFilter(logging.Filter):
    def __init__(self, level: int) -> None:
        super().__init__()
        self.level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= self.level


def _add_app_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    event_dict.setdefault("app_name", settings.app.name)
    event_dict.setdefault("app_version", settings.app.version)
    event_dict.setdefault("environment", "development" if settings.app.debug else "production")
    return event_dict


def _rename_event_key(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    if "event" in event_dict:
        event_dict["message"] = event_dict.pop("event")
    return event_dict


def _drop_color_message(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict


def _json_formatter() -> Any:
    return structlog.processors.JSONRenderer()


def _console_formatter() -> Any:
    return structlog.dev.ConsoleRenderer()


def setup_logging() -> None:
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        _add_app_context,
    ]

    if settings.app.debug:
        log_renderer = _console_formatter()
    else:
        log_renderer = _json_formatter()
        shared_processors.append(_drop_color_message)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            _rename_event_key,
            structlog.stdlib.ExtraAdder(),
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    log_level = logging.DEBUG if settings.app.debug else logging.INFO
    root_logger.setLevel(log_level)

    for name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True

    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.db.echo else logging.WARNING
    )

    # Подавление шумных сторонних логгеров
    for name in [
        "aiokafka",
        "kafka",
        "kafka.coordinator",
        "urllib3",
        "httpcore",
        "httpx",
        "celery",
        "asyncio",
    ]:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> Any:
    return structlog.get_logger(name)
