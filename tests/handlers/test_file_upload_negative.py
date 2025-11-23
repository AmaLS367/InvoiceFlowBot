"""
Negative test cases for file upload handlers: error handling.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handlers.file import handle_invoice_document, handle_invoice_photo
from tests.fakes.fake_ocr import FakeOcr
from tests.fakes.fake_services_drafts import FakeDraftService
from tests.fakes.fake_telegram import FakeDocument, FakeMessage, FakePhotoSize


def _get_fake_services(container: Any) -> tuple[FakeOcr, FakeDraftService]:
    """Helper to extract fake services from container."""
    # OCR is wrapped in a function, so we need to get it from invoice_service
    # For now, we'll access draft_service directly
    draft_service = container.draft_service
    assert isinstance(draft_service, FakeDraftService)
    # OCR is accessed through invoice_service._ocr_extractor which is a function
    # We'll check calls through the service
    return None, draft_service  # type: ignore[return-value]


@pytest.mark.asyncio
async def test_handle_invoice_document_without_document_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    """Test that handler handles missing document gracefully."""
    message = FakeMessage(
        text="",
        document=None,
    )

    await handle_invoice_document(message, file_handlers_data)

    assert len(message.answers) >= 1
    text = message.answers[0]["text"]
    assert isinstance(text, str)
    assert text != ""
    # Check that error message contains expected content
    assert "файл" in text.lower() or "не удалось" in text.lower()


@pytest.mark.asyncio
async def test_handle_invoice_document_ocr_failure_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    """Test that handler handles OCR failure gracefully."""
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

    # Mock save_file and make OCR fail
    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/fail.pdf"

        # Mock the OCR extractor to raise an error
        original_extractor = file_handlers_container.invoice_service._ocr_extractor

        async def failing_extractor(pdf_path: str, fast: bool = True, max_pages: int = 12) -> Any:
            raise RuntimeError("OCR failed")

        file_handlers_container.invoice_service._ocr_extractor = failing_extractor

        try:
            with patch("pathlib.Path.exists", return_value=True):
                with patch("pathlib.Path.suffix", return_value=".pdf"):
                    await handle_invoice_document(message, file_handlers_data)
        finally:
            # Restore original extractor
            file_handlers_container.invoice_service._ocr_extractor = original_extractor

    # Verify error message was sent
    assert len(message.answers) >= 1
    # Find error message (should be after "Получил файл" message)
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "распознава" in ans["text"].lower()
        and "недоступен" in ans["text"].lower()
        or "недоступен" in ans["text"].lower()
        or ("ошибка" in ans["text"].lower() and "получил" not in ans["text"].lower())
    ]
    # If no specific error message found, check all messages
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
    """Test that handler handles draft service failure gracefully."""
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

    # Set draft service to raise error
    draft_service.raise_error = True

    # Mock save_file
    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/draft_fail.pdf"

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.suffix", return_value=".pdf"):
                await handle_invoice_document(message, file_handlers_data)

    # Verify error message was sent
    assert len(message.answers) >= 1
    # Should have at least the "Получил файл" message and error message
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
    """Test that handler handles missing photo gracefully."""
    message = FakeMessage(
        text="",
        photos=[],
    )

    await handle_invoice_photo(message, file_handlers_data)

    assert len(message.answers) >= 1
    text = message.answers[0]["text"]
    assert isinstance(text, str)
    assert text != ""
    # Check that error message contains expected content
    assert "фото" in text.lower() or "не удалось" in text.lower()


@pytest.mark.asyncio
async def test_handle_invoice_photo_ocr_failure_sends_error(
    file_handlers_container: Any,
    file_handlers_data: Dict[str, Any],
) -> None:
    """Test that handler handles OCR failure for photos gracefully."""
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

    # Mock save_file and make OCR fail
    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/photo_fail.jpg"

        # Mock the OCR extractor to raise an error
        original_extractor = file_handlers_container.invoice_service._ocr_extractor

        async def failing_extractor(pdf_path: str, fast: bool = True, max_pages: int = 12) -> Any:
            raise RuntimeError("OCR failed")

        file_handlers_container.invoice_service._ocr_extractor = failing_extractor

        try:
            # Mock image processing
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
            # Restore original extractor
            file_handlers_container.invoice_service._ocr_extractor = original_extractor

    # Verify error message was sent
    assert len(message.answers) >= 1
    # Find error message (should be after "Получил файл" message)
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "распознава" in ans["text"].lower()
        and "недоступен" in ans["text"].lower()
        or "недоступен" in ans["text"].lower()
        or ("ошибка" in ans["text"].lower() and "получил" not in ans["text"].lower())
    ]
    # If no specific error message found, check all messages
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
    """Test that handler handles draft service failure for photos gracefully."""
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

    # Set draft service to raise error
    draft_service.raise_error = True

    # Mock save_file
    with patch("handlers.file.save_file", new_callable=AsyncMock) as mock_save_file:
        mock_save_file.return_value = "temp/photo_draft_fail.jpg"

        # Mock image processing
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

    # Verify error message was sent
    assert len(message.answers) >= 1
    # Should have at least the "Получил файл" message and error message
    error_messages = [
        ans["text"]
        for ans in message.answers
        if "черновик" in ans["text"].lower()
        or "ошибка" in ans["text"].lower()
        or "не удалось" in ans["text"].lower()
    ]
    assert len(error_messages) >= 1
