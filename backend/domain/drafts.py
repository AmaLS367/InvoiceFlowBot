from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from domain.invoices import Invoice


@dataclass
class InvoiceDraft:
    invoice: Invoice
    path: str
    raw_text: str = ""
    comments: List[str] = field(default_factory=list)


__all__ = ["InvoiceDraft"]
