"""
FSM state definitions used by the Telegram handlers.

Keeps all conversation states in a single place.
"""
from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class EditInvoiceState(StatesGroup):
    """
    States for editing the current invoice draft via reply messages.
    """

    waiting_for_field_value = State()
    waiting_for_comment = State()


class InvoicesPeriodState(StatesGroup):
    """
    States for collecting a date range from the user before listing invoices.
    """

    waiting_for_from_date = State()
    waiting_for_to_date = State()
    waiting_for_supplier = State()


__all__ = [
    "EditInvoiceState",
    "InvoicesPeriodState",
]

