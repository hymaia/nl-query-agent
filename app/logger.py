import logging
import sys

from pythonjsonlogger.json import JsonFormatter

from app.config import settings


def setup_uvicorn_json_logging() -> None:
    json_formatter = JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(json_formatter)

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.handlers = [handler]
        uvicorn_logger.propagate = False


def setup_logger() -> logging.Logger:
    logger = logging.getLogger("nl-sql-agent")
    logger.setLevel(settings.log_level.upper())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.propagate = False
    return logger


logger = setup_logger()
