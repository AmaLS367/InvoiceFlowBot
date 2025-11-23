"""
Callback handlers orchestrator.

Registers all callback handlers from submodules.
"""
from aiogram import Router

from handlers.callbacks_edit import setup as setup_edit
from handlers.callbacks_misc import setup as setup_misc

router = Router()

setup_edit(router)
setup_misc(router)
