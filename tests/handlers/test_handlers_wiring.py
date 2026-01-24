from aiogram import Router

from backend.handlers import callbacks, commands


def test_commands_router_is_defined() -> None:
    assert hasattr(commands, "router")
    assert isinstance(commands.router, Router)


def test_callbacks_router_is_defined() -> None:
    assert hasattr(callbacks, "router")
    assert isinstance(callbacks.router, Router)
