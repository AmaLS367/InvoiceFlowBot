from __future__ import annotations

from aiogram.fsm.state import State, StatesGroup


class EditInvoiceState(StatesGroup):
    """
    FSM states used when the user edits the current invoice draft.
    """

    waiting_for_field_value = State()
    waiting_for_comment = State()


class InvoicesPeriodState(StatesGroup):
    """
    FSM states used when the user configures a date period for invoices listing.
    """

    waiting_for_from_date = State()
    waiting_for_to_date = State()
    waiting_for_supplier = State()


__all__ = [
    "EditInvoiceState",
    "InvoicesPeriodState",
]

