from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers.file import handle_invoice_document, handle_invoice_photo
from tests.fakes.fake_services_drafts import FakeDraftService
from tests.fakes.fake_telegram import FakeDocument, FakeMessage, FakePhotoSize


@pytest.mark.asyncio
async def test_handle_invoice_document_without_document_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    message = FakeMessage(
        text="",
        document=None,
    )

    await handle_invoice_document(message, file_handlers_data)

    assert len(message.answers) >= 1
    text = message.answers[0]["text"]
    assert isinstance(text, str)
    assert text != ""
    assert "файл" in text.lower() or "не удалось" in text.lower()


@pytest.mark.asyncio
async def test_handle_invoice_document_ocr_failure_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    draft_service = file_handlers_container.draft_service
    assert isinstance(draft_service, FakeDraftService)

    document = FakeDocument(
        file_id="file_ocr_fail",
        file_name="fail.pdf",
        mime_type="application/pdf",
    )

    fake_bot = MagicMock()
    fake_file = MagicMock()
    fake_file.file_path = "documents/fail.pdf"
    fake_bot.get_file = AsyncMock(return_value=fake_file)
    fake_bot.download_file = AsyncMock()

    message = FakeMessage(
        text="",
        document=document,
        bot=fake_bot,
    )

    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/fail.pdf"

        original_extractor = file_handlers_container.invoice_service._ocr_extractor

        async def failing_extractor(pdf_path: str, fast: bool = True, max_pages: int = 12) -> Any:
            raise RuntimeError("OCR failed")

        file_handlers_container.invoice_service._ocr_extractor = failing_extractor

        try:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.suffix", return_value=".pdf"):
                    await handle_invoice_document(message, file_handlers_data)
        finally:
            file_handlers_container.invoice_service._ocr_extractor = original_extractor

    assert len(message.answers) >= 1
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "распознава" in ans["text"].lower()
        and "недоступен" in ans["text"].lower()
        or "недоступен" in ans["text"].lower()
        or ("ошибка" in ans["text"].lower() and "получил" not in ans["text"].lower())
    ]
    if not error_messages:
        all_texts = " ".join([ans["text"] for ans in message.answers])
        assert "недоступен" in all_texts.lower() or "распознава" in all_texts.lower()
    else:
        assert len(error_messages) >= 1


@pytest.mark.asyncio
async def test_handle_invoice_document_draft_failure_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    draft_service = file_handlers_container.draft_service
    assert isinstance(draft_service, FakeDraftService)

    document = FakeDocument(
        file_id="file_draft_fail",
        file_name="draft_fail.pdf",
        mime_type="application/pdf",
    )

    fake_bot = MagicMock()
    fake_file = MagicMock()
    fake_file.file_path = "documents/draft_fail.pdf"
    fake_bot.get_file = AsyncMock(return_value=fake_file)
    fake_bot.download_file = AsyncMock()

    message = FakeMessage(
        text="",
        document=document,
        bot=fake_bot,
    )

    draft_service.raise_error = True

    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/draft_fail.pdf"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", return_value=".pdf"):
                await handle_invoice_document(message, file_handlers_data)

    assert len(message.answers) >= 1
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "черновик" in ans["text"].lower()
        or "ошибка" in ans["text"].lower()
        or "не удалось" in ans["text"].lower()
    ]
    assert len(error_messages) >= 1


@pytest.mark.asyncio
async def test_handle_invoice_photo_without_photo_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    message = FakeMessage(
        text="",
        photos=[],
    )

    await handle_invoice_photo(message, file_handlers_data)

    assert len(message.answers) >= 1
    text = message.answers[0]["text"]
    assert isinstance(text, str)
    assert text != ""
    assert "фото" in text.lower() or "не удалось" in text.lower()


@pytest.mark.asyncio
async def test_handle_invoice_photo_ocr_failure_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    draft_service = file_handlers_container.draft_service
    assert isinstance(draft_service, FakeDraftService)

    photos = [
        FakePhotoSize(file_id="photo_fail", width=800, height=600),
    ]

    fake_bot = MagicMock()
    fake_file = MagicMock()
    fake_file.file_path = "photos/photo_fail.jpg"
    fake_bot.get_file = AsyncMock(return_value=fake_file)
    fake_bot.download_file = AsyncMock()

    message = FakeMessage(
        text="",
        photos=photos,
        bot=fake_bot,
    )

    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/photo_fail.jpg"

        original_extractor = file_handlers_container.invoice_service._ocr_extractor

        async def failing_extractor(pdf_path: str, fast: bool = True, max_pages: int = 12) -> Any:
            raise RuntimeError("OCR failed")

        file_handlers_container.invoice_service._ocr_extractor = failing_extractor

        try:
            with patch("PIL.Image.open") as mock_image_open:
                mock_image = MagicMock()
                mock_image_open.return_value = mock_image
                mock_image.convert.return_value = mock_image
                mock_image.save = MagicMock()

                with patch("pathlib.Path.exists", return_value=True):
                    with patch("pathlib.Path.suffix", return_value=".jpg"):
                        with patch(
                            "pathlib.Path.with_suffix", return_value=Path("temp/photo_fail.jpg")
                        ):
                            await handle_invoice_photo(message, file_handlers_data)
        finally:
            file_handlers_container.invoice_service._ocr_extractor = original_extractor

    assert len(message.answers) >= 1
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "распознава" in ans["text"].lower()
        and "недоступен" in ans["text"].lower()
        or "недоступен" in ans["text"].lower()
        or ("ошибка" in ans["text"].lower() and "получил" not in ans["text"].lower())
    ]
    if not error_messages:
        all_texts = " ".join([ans["text"] for ans in message.answers])
        assert "недоступен" in all_texts.lower() or "распознава" in all_texts.lower()
    else:
        assert len(error_messages) >= 1


@pytest.mark.asyncio
async def test_handle_invoice_photo_draft_failure_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    draft_service = file_handlers_container.draft_service
    assert isinstance(draft_service, FakeDraftService)

    photos = [
        FakePhotoSize(file_id="photo_draft_fail", width=800, height=600),
    ]

    fake_bot = MagicMock()
    fake_file = MagicMock()
    fake_file.file_path = "photos/photo_draft_fail.jpg"
    fake_bot.get_file = AsyncMock(return_value=fake_file)
    fake_bot.download_file = AsyncMock()

    message = FakeMessage(
        text="",
        photos=photos,
        bot=fake_bot,
    )

    draft_service.raise_error = True

    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/photo_draft_fail.jpg"

        with patch("PIL.Image.open") as mock_image_open:
            mock_image = MagicMock()
            mock_image_open.return_value = mock_image
            mock_image.convert.return_value = mock_image
            mock_image.save = MagicMock()

            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.suffix", return_value=".jpg"):
                    with patch(
                        "pathlib.Path.with_suffix", return_value=Path("temp/photo_draft_fail.jpg")
                    ):
                        await handle_invoice_photo(message, file_handlers_data)

    assert len(message.answers) >= 1
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "черновик" in ans["text"].lower()
        or "ошибка" in ans["text"].lower()
        or "не удалось" in ans["text"].lower()
    ]
    assert len(error_messages) >= 1
