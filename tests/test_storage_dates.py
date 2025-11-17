import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("BOT_TOKEN", "test-token")

from storage import db  # noqa: E402


def test_to_iso_handles_numeric_and_locale_dates():
    assert db._to_iso("12.06.2025") == "2025-06-12"
    assert db._to_iso("5 July 24") == "2024-07-05"


def test_to_iso_returns_none_for_invalid_formats():
    assert db._to_iso("not a date") is None
    assert db._to_iso("") is None

