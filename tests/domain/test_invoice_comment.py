from datetime import datetime

from backend.domain.invoices import InvoiceComment


def test_invoice_comment_basic_creation() -> None:
    created_at = datetime(2024, 1, 15, 10, 30, 0)
    comment = InvoiceComment(
        author="Test User",
        message="This is a test comment",
        created_at=created_at,
    )

    assert comment.author == "Test User"
    assert comment.message == "This is a test comment"
    assert comment.created_at == created_at
    assert isinstance(comment.created_at, datetime)


def test_invoice_comment_optional_fields() -> None:
    comment = InvoiceComment(message="Comment without author")

    assert comment.message == "Comment without author"
    assert comment.author is None
    assert comment.created_at is None


def test_invoice_comment_with_datetime_variations() -> None:
    datetimes = [
        datetime(2024, 1, 1, 0, 0, 0),
        datetime(2024, 12, 31, 23, 59, 59),
        datetime(2020, 6, 15, 12, 30, 45),
    ]
    for created_at in datetimes:
        comment = InvoiceComment(
            message="Test",
            author="User",
            created_at=created_at,
        )
        assert comment.created_at == created_at
        assert isinstance(comment.created_at, datetime)


def test_invoice_comment_with_unicode_and_special_characters() -> None:
    comment = InvoiceComment(
        message="Comment with: émojis 🎉, unicode 测试, and symbols !@#$%",
        author="User-测试",
    )

    assert comment.message == "Comment with: émojis 🎉, unicode 测试, and symbols !@#$%"
    assert comment.author == "User-测试"
