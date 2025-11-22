import json
from pathlib import Path

from ocr.engine import util


def test_file_sha256_matches_known_value(tmp_path: Path) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("invoice-123", encoding="utf-8")

    assert (
        util.file_sha256(str(file_path))
        == "b66e5d8a3f966ab97a07d5c250d32315a12eccf733119756c85fd24e4d1d5ffb"
    )


def test_write_json_creates_parent_directory(tmp_path: Path) -> None:
    nested_path = tmp_path / "nested" / "data.json"

    util.write_json(str(nested_path), {"ok": True})

    assert nested_path.exists()
    assert json.loads(nested_path.read_text(encoding="utf-8")) == {"ok": True}
