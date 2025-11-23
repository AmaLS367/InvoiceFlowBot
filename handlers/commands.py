"""
Command handlers orchestrator.

Registers all command handlers from submodules.
"""

from aiogram import Router

from handlers.commands_common import setup as setup_common
from handlers.commands_drafts import setup as setup_drafts
from handlers.commands_invoices import setup as setup_invoices

router = Router()

setup_common(router)
setup_drafts(router)
setup_invoices(router)
