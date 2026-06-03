from pathlib import Path

from backend import config


def test_resolve_db_path_relative_to_backend_dir() -> None:
    resolved = config.resolve_db_path("../data.sqlite")

    expected = (Path(config.__file__).resolve().parent / "../data.sqlite").resolve()
    assert resolved == expected


def test_resolve_db_path_keeps_absolute_paths() -> None:
    absolute = Path("C:/tmp/invoiceflowbot.sqlite").resolve()

    resolved = config.resolve_db_path(str(absolute))

    assert resolved == absolute
