import json
from pathlib import Path

from backend.ocr.engine import util


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


def test_ensure_dir_creates_directory(tmp_path: Path) -> None:
    """Test ensure_dir function."""
    dir_path = tmp_path / "test_dir"
    util.ensure_dir(str(dir_path))
    assert dir_path.exists()
    assert dir_path.is_dir()


def test_set_request_id():
    """Test set_request_id function."""
    util.set_request_id("test-request-123")
    # Request ID is stored in context var, can't easily test without accessing internals
    # But we can verify it doesn't raise
    util.set_request_id("another-request")


def test_get_logger():
    """Test get_logger function."""
    logger = util.get_logger("test.logger")
    assert logger is not None
    assert logger.name == "test.logger"


def test_get_logger_default():
    """Test get_logger with default name."""
    logger = util.get_logger()
    assert logger is not None
    assert logger.name == "ocr.engine"
