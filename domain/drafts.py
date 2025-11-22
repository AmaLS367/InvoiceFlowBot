from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from domain.invoices import Invoice


@dataclass
class InvoiceDraft:
    """
    Domain object representing a current invoice draft for a user.

    It keeps the parsed Invoice together with source file path,
    optional raw OCR text and user comments that are not yet persisted.
    """

    invoice: Invoice
    path: str
    raw_text: str = ""
    comments: List[str] = field(default_factory=list)


__all__ = ["InvoiceDraft"]

