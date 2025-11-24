from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers.file import handle_invoice_document, handle_invoice_photo
from tests.fakes.fake_ocr import FakeOcr
from tests.fakes.fake_services_drafts import FakeDraftService
from tests.fakes.fake_telegram import FakeDocument, FakeMessage, FakePhotoSize


@pytest.mark.asyncio
async def test_handle_invoice_document_happy_path(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    draft_service = file_handlers_container.draft_service
    assert isinstance(draft_service, FakeDraftService)

    document = FakeDocument(
        file_id="file_123",
        file_name="test_invoice.pdf",
        mime_type="application/pdf",
    )

    fake_bot = MagicMock()
    fake_file = MagicMock()
    fake_file.file_path = "documents/test_invoice.pdf"
    fake_bot.get_file = AsyncMock(return_value=fake_file)
    fake_bot.download_file = AsyncMock()

    message = FakeMessage(
        text="",
        document=document,
        bot=fake_bot,
    )

    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/test_invoice.pdf"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", return_value=".pdf"):
                await handle_invoice_document(message, file_handlers_data)

    assert len(draft_service.calls) >= 1
    set_draft_calls = [c for c in draft_service.calls if c.get("method") == "set_current_draft"]
    assert len(set_draft_calls) >= 1

    assert len(message.answers) >= 1
    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""


@pytest.mark.asyncio
async def test_handle_invoice_photo_happy_path(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    draft_service = file_handlers_container.draft_service
    assert isinstance(draft_service, FakeDraftService)

    photos = [
        FakePhotoSize(file_id="photo_small", width=320, height=240),
        FakePhotoSize(file_id="photo_big", width=1024, height=768),
    ]

    fake_bot = MagicMock()
    fake_file = MagicMock()
    fake_file.file_path = "photos/test_photo.jpg"
    fake_bot.get_file = AsyncMock(return_value=fake_file)
    fake_bot.download_file = AsyncMock()

    message = FakeMessage(
        text="",
        photos=photos,
        bot=fake_bot,
    )

    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/test_photo.jpg"

        with patch("PIL.Image.open") as mock_image_open:
            mock_image = MagicMock()
            mock_image_open.return_value = mock_image
            mock_image.convert.return_value = mock_image
            mock_image.save = MagicMock()

            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.suffix", return_value=".jpg"):
                    with patch(
                        "pathlib.Path.with_suffix", return_value=Path("temp/test_photo.jpg")
                    ):
                        await handle_invoice_photo(message, file_handlers_data)

    assert len(draft_service.calls) >= 1
    set_draft_calls = [c for c in draft_service.calls if c.get("method") == "set_current_draft"]
    assert len(set_draft_calls) >= 1

    assert len(message.answers) >= 1
    first_answer = message.answers[0]["text"]
    assert isinstance(first_answer, str)
    assert first_answer != ""
