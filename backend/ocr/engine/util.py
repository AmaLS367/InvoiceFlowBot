import hashlib
import json
import logging
import os
import time
import traceback
from contextlib import contextmanager
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

import config

_req_var: ContextVar[str] = ContextVar("req", default="-")
_configured = False


class RequestFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.req = _req_var.get()
        return True


class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "req", "-"),
            "message": record.getMessage(),
        }

        # Add extra fields
        if hasattr(record, "funcName"):
            log_data["function"] = record.funcName
        if hasattr(record, "lineno"):
            log_data["line"] = record.lineno
        if hasattr(record, "pathname"):
            log_data["file"] = record.pathname

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": traceback.format_exception(*record.exc_info),
            }

        # Add custom fields from extra parameter
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
                "req",
                "taskName",
            ]:
                log_data[key] = value

        return json.dumps(log_data, ensure_ascii=False, default=str)


def file_sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def write_json(path: str, data: Any) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def set_request_id(req: str) -> None:
    _req_var.set(req)


def _log_dir() -> Path:
    root = Path(__file__).resolve().parents[2]
    d = Path(config.LOG_DIR) if config.LOG_DIR else (root / "logs")
    d.mkdir(parents=True, exist_ok=True)
    return d


def configure_logging() -> None:
    global _configured
    if _configured:
        return
    level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    log_dir = _log_dir()
    max_bytes = config.LOG_ROTATE_MB * 1024 * 1024
    backups = config.LOG_BACKUPS
    to_console = config.LOG_CONSOLE

    # Use JSON formatter for structured logging
    json_fmt = JsonFormatter()
    req_filter = RequestFilter()

    root = logging.getLogger()
    root.setLevel(level)

    common = RotatingFileHandler(
        log_dir / "ocr_engine.log", maxBytes=max_bytes, backupCount=backups, encoding="utf-8"
    )
    common.setLevel(level)
    common.setFormatter(json_fmt)
    common.addFilter(req_filter)
    root.addHandler(common)

    errors = RotatingFileHandler(
        log_dir / "errors.log", maxBytes=max_bytes, backupCount=backups, encoding="utf-8"
    )
    errors.setLevel(logging.WARNING)
    errors.setFormatter(json_fmt)
    errors.addFilter(req_filter)
    root.addHandler(errors)

    if to_console:
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(json_fmt)
        ch.addFilter(req_filter)
        root.addHandler(ch)

    router = logging.getLogger("ocr.router")
    router.setLevel(logging.DEBUG)
    h_router = RotatingFileHandler(
        log_dir / "router.log", maxBytes=max_bytes, backupCount=backups, encoding="utf-8"
    )
    h_router.setLevel(logging.DEBUG)
    h_router.setFormatter(json_fmt)
    h_router.addFilter(req_filter)
    router.addHandler(h_router)
    router.propagate = True

    extract = logging.getLogger("ocr.extract")
    extract.setLevel(logging.DEBUG)
    h_extract = RotatingFileHandler(
        log_dir / "extract.log", maxBytes=max_bytes, backupCount=backups, encoding="utf-8"
    )
    h_extract.setLevel(logging.DEBUG)
    h_extract.setFormatter(json_fmt)
    h_extract.addFilter(req_filter)
    extract.addHandler(h_extract)
    extract.propagate = True

    _configured = True


def get_logger(name: str = "ocr.engine") -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)


@contextmanager
def time_block(logger: logging.Logger, label: str, level: int = logging.DEBUG):
    t0 = time.perf_counter()
    try:
        yield
    finally:
        dt = (time.perf_counter() - t0) * 1000.0
        logger.log(level, f"{label} took {dt:.1f} ms")


async def save_file(src: Any, bot: Any) -> Optional[str]:
    from aiogram.types import PhotoSize

    tg_file = await bot.get_file(src.file_id)
    if not tg_file or not tg_file.file_path:
        return None

    orig_name = getattr(src, "file_name", None)
    ext = Path(tg_file.file_path).suffix.lower()
    if not ext:
        ext = Path(orig_name).suffix.lower() if orig_name else ""
    if not ext:
        ext = ".jpg" if isinstance(src, PhotoSize) else ".bin"

    stem = (
        Path(orig_name).stem if orig_name else ("photo" if isinstance(src, PhotoSize) else "file")
    )

    os.makedirs("temp", exist_ok=True)
    local_path = Path("temp") / f"{stem}_{src.file_id[:8]}{ext}"
    await bot.download_file(tg_file.file_path, destination=str(local_path))
    return str(local_path)
