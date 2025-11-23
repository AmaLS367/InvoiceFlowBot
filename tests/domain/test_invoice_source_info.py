"""
Unit tests for InvoiceSourceInfo domain entity.
"""

from domain.invoices import InvoiceSourceInfo


def test_invoice_source_info_basic_creation() -> None:
    """
    InvoiceSourceInfo should keep file and provider metadata.
    """
    source = InvoiceSourceInfo(
        file_path="/tmp/invoice.pdf",
        file_sha256="abc123def456",
        provider="mindee",
        raw_payload_path="/tmp/invoice.json",
    )

    assert source.file_path == "/tmp/invoice.pdf"
    assert source.file_sha256 == "abc123def456"
    assert source.provider == "mindee"
    assert source.raw_payload_path == "/tmp/invoice.json"

    assert isinstance(source.file_path, str)
    assert isinstance(source.file_sha256, str)
    assert isinstance(source.provider, str)
    assert isinstance(source.raw_payload_path, str)


def test_invoice_source_info_defaults_are_none() -> None:
    """
    All fields in InvoiceSourceInfo should default to None when not provided.
    """
    source = InvoiceSourceInfo()

    assert source.file_path is None
    assert source.file_sha256 is None
    assert source.provider is None
    assert source.raw_payload_path is None


def test_invoice_source_info_with_different_providers() -> None:
    """
    InvoiceSourceInfo should support different OCR providers.
    """
    providers = ["mindee", "deepseek", "gemini", "openai", "custom"]
    for provider in providers:
        source = InvoiceSourceInfo(provider=provider)
        assert source.provider == provider


def test_invoice_source_info_with_file_paths() -> None:
    """
    InvoiceSourceInfo should handle different file path formats.
    """
    paths = [
        "/tmp/invoice.pdf",
        "C:\\Users\\Documents\\invoice.pdf",
        "./relative/path/invoice.pdf",
        "https://example.com/invoice.pdf",
    ]
    for file_path in paths:
        source = InvoiceSourceInfo(file_path=file_path)
        assert source.file_path == file_path
