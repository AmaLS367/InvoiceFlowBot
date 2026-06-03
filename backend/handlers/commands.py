"""
Command handlers orchestrator.

Registers all command handlers from submodules.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from backend.core.container import AppContainer
from backend.handlers.commands_common import setup as setup_common
from backend.handlers.commands_drafts import handle_force_reply
from backend.handlers.commands_drafts import setup as setup_drafts
from backend.handlers.commands_invoices import (
    handle_force_reply_invoices,
)
from backend.handlers.commands_invoices import (
    setup as setup_invoices,
)

router = Router()


def setup_reply_dispatcher(router: Router) -> None:
    """Register a shared force-reply dispatcher across command modules."""

    @router.message(F.reply_to_message)
    async def on_force_reply_dispatch(
        message: Message,
        state: FSMContext,
        container: AppContainer,
    ) -> None:
        if await handle_force_reply(message, state, container):
            return
        await handle_force_reply_invoices(message, state, container)


setup_common(router)
setup_drafts(router, include_reply_handler=False)
setup_invoices(router, include_reply_handler=False)
setup_reply_dispatcher(router)
