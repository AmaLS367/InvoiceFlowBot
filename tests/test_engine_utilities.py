import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("BOT_TOKEN", "test-token")

from ocr.engine import util  # noqa: E402


def test_file_sha256_matches_known_value(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("invoice-123", encoding="utf-8")
    assert util.file_sha256(str(file_path)) == "b66e5d8a3f966ab97a07d5c250d32315a12eccf733119756c85fd24e4d1d5ffb"


def test_write_json_creates_parent_directory(tmp_path: Path):
    nested_path = tmp_path / "nested" / "data.json"
    util.write_json(str(nested_path), {"ok": True})
    assert nested_path.exists()
    assert json.loads(nested_path.read_text(encoding="utf-8")) == {"ok": True}

