from __future__ import annotations

from typing import Any, Dict, List, Optional


class FakeUser:
    def __init__(
        self,
        user_id: int = 1,
        username: Optional[str] = None,
    ) -> None:
        self.id = user_id
        self.username = username


class FakeDocument:
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
        self.answers.append({"text": text, "kwargs": kwargs})

    async def reply(self, text: str, **kwargs: Any) -> None:
        await self.answer(text, **kwargs)

    async def answer_document(self, document: Any, **kwargs: Any) -> None:
        self.answers.append({"document": document, "kwargs": kwargs})

    async def edit_reply_markup(self, reply_markup: Any = None) -> None:
        self.answers.append({"edit_reply_markup": True, "reply_markup": reply_markup})


class FakeCallbackQuery:
    def __init__(
        self,
        data: str,
        user_id: int = 1,
        message: Optional[FakeMessage] = None,
    ) -> None:
        self.data = data
        self.from_user = FakeUser(user_id=user_id)
        self.message = message or FakeMessage()
        self.answered = False
        self.answer_text: Optional[str] = None

    async def answer(self, text: Optional[str] = None, **kwargs: Any) -> None:
        self.answered = True
        self.answer_text = text
