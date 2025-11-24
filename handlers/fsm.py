"""
FSM state definitions used by the Telegram handlers.

Keeps all conversation states in a single place.
"""

from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class EditInvoiceState(StatesGroup):
    waiting_for_field_value = State()
    waiting_for_comment = State()


class InvoicesPeriodState(StatesGroup):
    waiting_for_from_date = State()
    waiting_for_to_date = State()
    waiting_for_supplier = State()


__all__ = [
    "EditInvoiceState",
    "InvoicesPeriodState",
]
