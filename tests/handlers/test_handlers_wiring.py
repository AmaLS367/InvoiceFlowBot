"""
Smoke tests for handlers wiring and router structure.
"""

from aiogram import Router

from handlers import callbacks, commands


def test_commands_router_is_defined() -> None:
    """Test that commands router is defined and is a Router instance."""
    assert hasattr(commands, "router")
    assert isinstance(commands.router, Router)


def test_callbacks_router_is_defined() -> None:
    """Test that callbacks router is defined and is a Router instance."""
    assert hasattr(callbacks, "router")
    assert isinstance(callbacks.router, Router)
