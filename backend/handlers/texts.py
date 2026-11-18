"""Localizable text and formatting helpers for Telegram handlers."""

from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from importlib.resources import files
from typing import Iterator, cast

DEFAULT_LOCALE = "ru"
LANGUAGES = {"ru": "Русский", "en": "English"}
PLACEHOLDER = "—"
SECTION_DIVIDER = "—" * 34

_CATALOGS = {
    locale: cast(
        dict[str, str],
        json.loads(
            files("backend.handlers").joinpath("locales", f"{locale}.json").read_text("utf-8")
        ),
    )
    for locale in LANGUAGES
}
_current_locale = ContextVar("locale", default=DEFAULT_LOCALE)

_HEADER_FIELDS = {
    "supplier": "HEADER_FIELD_SUPPLIER",
    "client": "HEADER_FIELD_CLIENT",
    "date": "HEADER_FIELD_DATE",
    "doc_number": "HEADER_FIELD_NUMBER",
    "total_sum": "SUMMARY_TOTAL",
}
_ITEM_FIELDS = {
    "name": "ITEM_NAME",
    "qty": "ITEM_QTY",
    "price": "ITEM_PRICE",
    "total": "ITEM_TOTAL",
}


def resolve_locale(preferred: str | None, telegram_language: str | None) -> str:
    if preferred is not None and preferred in LANGUAGES:
        return preferred
    if telegram_language:
        base = telegram_language.lower().replace("_", "-").split("-", 1)[0]
        if base in LANGUAGES:
            return base
    return DEFAULT_LOCALE


@contextmanager
def use_locale(locale: str) -> Iterator[None]:
    token = _current_locale.set(locale)
    try:
        yield
    finally:
        _current_locale.reset(token)


def t(key: str, *, locale: str | None = None, **values: object) -> str:
    catalog = _CATALOGS[locale or _current_locale.get()]
    template = catalog[key] if key in catalog else _CATALOGS[DEFAULT_LOCALE][key]
    return template.format(**values) if values else template


def ocr_review_reason(code: str) -> str:
    key = f"OCR_REVIEW_REASON_{code.upper()}"
    if key not in _CATALOGS[DEFAULT_LOCALE]:
        key = "OCR_REVIEW_UNKNOWN_REASON"
    return t(key)


def save_success(invoice_id: int) -> str:
    return t("SAVE_SUCCESS", invoice_id=invoice_id)


def auto_sum_mismatch_comment(
    sum_items: float,
    header_sum: float,
    diff: float,
    doc_number: str,
    supplier: str,
) -> str:
    return t(
        "AUTO_SUM_MISMATCH_COMMENT",
        sum_items=sum_items,
        header_sum=header_sum,
        diff=diff,
        doc_number=doc_number,
        supplier=supplier,
    )


def edit_enter_header_value(field: str) -> str:
    return t("EDIT_ENTER_HEADER_VALUE", field_label=t(_HEADER_FIELDS[field]))


def edit_enter_item_value(field: str, idx: int) -> str:
    return t("EDIT_ENTER_ITEM_VALUE", field_label=t(_ITEM_FIELDS[field]), idx=idx)


def format_item_edit_card(
    idx: int,
    name: str,
    code: str,
    qty: str,
    price: str,
    total: str,
) -> str:
    return (
        f"#{idx}\n"
        f"{t('ITEM_NAME')}: {name}\n"
        f"{t('ITEM_CODE')}: {code}\n"
        f"{t('ITEM_QTY')}: {qty} | {t('ITEM_PRICE')}: {price} | {t('ITEM_TOTAL')}: {total}"
    )


def invoices_period_header(from_text: str, to_text: str, supplier: str | None) -> str:
    if supplier:
        return t(
            "INVOICES_PERIOD_WITH_SUPPLIER", from_text=from_text, to_text=to_text, supplier=supplier
        )
    return t("INVOICES_PERIOD_HEADER", from_text=from_text, to_text=to_text)
