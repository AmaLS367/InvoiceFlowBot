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


class FakeDocument:
    """Fake Telegram document for testing."""

    def __init__(
        self,
        file_id: str,
        file_name: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> None:
        self.file_id = file_id
        self.file_name = file_name
        self.mime_type = mime_type


class FakePhotoSize:
    """Fake Telegram photo size for testing."""

    def __init__(
        self,
        file_id: str,
        width: int,
        height: int,
    ) -> None:
        self.file_id = file_id
        self.width = width
        self.height = height


class FakeMessage:
    """Fake Telegram message for testing."""

    def __init__(
        self,
        text: str = "",
        user_id: int = 1,
        chat_id: int = 1,
        document: Optional[FakeDocument] = None,
        photos: Optional[List[FakePhotoSize]] = None,
        bot: Any = None,
    ) -> None:
        self.text = text
        self.from_user = FakeUser(user_id=user_id)
        self.chat = type("Chat", (), {"id": chat_id})()
        self.document = document
        self.photo = photos or []
        self.bot = bot
        self.answers: List[Dict[str, Any]] = []

    async def answer(self, text: str, **kwargs: Any) -> None:
        """Fake answer method that stores sent messages."""
        self.answers.append({"text": text, "kwargs": kwargs})

    async def reply(self, text: str, **kwargs: Any) -> None:
        """Fake reply method that stores sent messages."""
        await self.answer(text, **kwargs)

    async def answer_document(self, document: Any, **kwargs: Any) -> None:
        """Fake answer_document method that stores sent documents."""
        self.answers.append({"document": document, "kwargs": kwargs})
