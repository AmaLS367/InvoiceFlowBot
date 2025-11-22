from storage import db


def test_to_iso_handles_numeric_and_locale_dates():
    assert db.to_iso("12.06.2025") == "2025-06-12"
    assert db.to_iso("5 July 24") == "2024-07-05"


def test_to_iso_returns_none_for_invalid_formats():
    assert db.to_iso("not a date") is None
    assert db.to_iso("") is None

