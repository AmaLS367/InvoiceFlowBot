"""
Fake Telegram entities for testing handlers without real Telegram API.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class FakeUser:
    """Fake Telegram user for testing."""

    def __init__(
        self,
        user_id: int = 1,
        username: Optional[str] = None,
    ) -> None:
        self.id = user_id
        self.username = username


class FakeMessage:
    """Fake Telegram message for testing."""

    def __init__(
        self,
        text: str,
        user_id: int = 1,
        chat_id: int = 1,
    ) -> None:
        self.text = text
        self.from_user = FakeUser(user_id=user_id)
        self.chat = type("Chat", (), {"id": chat_id})()
        self.answers: List[Dict[str, Any]] = []

    async def answer(self, text: str, **kwargs: Any) -> None:
        """Fake answer method that stores sent messages."""
        self.answers.append({"text": text, "kwargs": kwargs})

