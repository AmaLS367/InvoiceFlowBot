import importlib
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def ensure_test_env() -> None:
    os.environ.setdefault("BOT_TOKEN", "test-token")


def test_core_modules_importable():
    ensure_test_env()
    modules = (
        "bot",
        "config",
        "ocr.extract",
        "ocr.engine.router",
        "handlers.utils",
        "storage.db",
    )
    for name in modules:
        module = importlib.import_module(name)
        assert module is not None, f"Module {name} should import successfully"

