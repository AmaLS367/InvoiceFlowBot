"""
Pytest configuration for all tests.
"""
import sys
from pathlib import Path

# Add project root to Python path for imports
# This must happen before any imports from the project
project_root = Path(__file__).parent.parent.resolve()
project_root_str = str(project_root)
if project_root_str not in sys.path:
    sys.path.insert(0, project_root_str)

import pytest  # noqa: E402

from config import Settings  # noqa: E402
from core.container import AppContainer  # noqa: E402
from handlers.di_middleware import ContainerMiddleware  # noqa: E402
from storage.db_async import AsyncInvoiceStorage  # noqa: E402
from tests.fakes.fake_ocr import FakeOcr, make_fake_ocr_extractor  # noqa: E402
from tests.fakes.fake_storage import (  # noqa: E402
    FakeStorage,
    make_fake_delete_draft_func,
    make_fake_fetch_invoices_func,
    make_fake_load_draft_func,
    make_fake_save_draft_func,
    make_fake_save_invoice_func,
)
from tests.utils.alembic_test_utils import run_migrations_for_url  # noqa: E402


@pytest.fixture()
def app_config() -> Settings:
    """Create a test configuration."""
    return Settings()  # type: ignore[call-arg]


@pytest.fixture()
def fake_storage() -> FakeStorage:
    """Create a fake storage instance."""
    return FakeStorage()


@pytest.fixture()
def fake_ocr() -> FakeOcr:
    """Create a fake OCR instance."""
    return FakeOcr()


@pytest.fixture()
def app_container(
    app_config: Settings,
    fake_storage: FakeStorage,
    fake_ocr: FakeOcr,
) -> AppContainer:
    """Create an AppContainer with fake dependencies."""
    return AppContainer(
        config=app_config,
        ocr_extractor=make_fake_ocr_extractor(fake_ocr),
        save_invoice_func=make_fake_save_invoice_func(fake_storage),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage),
        load_draft_func=make_fake_load_draft_func(fake_storage),
        save_draft_func=make_fake_save_draft_func(fake_storage),
        delete_draft_func=make_fake_delete_draft_func(fake_storage),
    )


@pytest.fixture()
def container_middleware(app_container: AppContainer) -> ContainerMiddleware:
    """Create a ContainerMiddleware with the test container."""
    return ContainerMiddleware(container=app_container)


@pytest.fixture()
def test_db_path(tmp_path: Path) -> Path:
    """Create a temporary SQLite database file path for testing."""
    db_path = tmp_path / "test_db.sqlite3"
    return db_path


@pytest.fixture()
def migrated_database_url(test_db_path: Path) -> str:
    """
    Create a database URL and run Alembic migrations against it.

    Returns:
        Database URL string (sqlite:///path/to/db.sqlite3).
    """
    database_url = f"sqlite:///{test_db_path}"

    run_migrations_for_url(database_url)

    return database_url


@pytest.fixture()
def async_storage_with_migrations(migrated_database_url: str) -> AsyncInvoiceStorage:
    """
    Create an AsyncInvoiceStorage instance with a migrated database.

    The database file is created in a temporary directory and migrations
    are run before the storage instance is created.
    """
    # Extract file path from sqlite:/// URL
    db_path = migrated_database_url.replace("sqlite:///", "")
    storage = AsyncInvoiceStorage(database_path=db_path)
    return storage


@pytest.fixture()
def app_config_with_test_db(migrated_database_url: str) -> Settings:
    """
    Create a Settings instance with the test database path configured.

    Note: Settings uses DB_FILENAME and DB_DIR, so we need to extract
    the path from the URL and set it appropriately.
    """
    # Create a minimal settings object for testing
    # Note: Settings fields are read-only after creation, so we can't modify them directly.
    # The database path should be used directly via async_storage_with_migrations fixture.
    config = Settings()  # type: ignore[call-arg]
    return config


@pytest.fixture()
def app_container_with_test_db(
    app_config_with_test_db: Settings,
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> AppContainer:
    """
    Create an AppContainer with test database storage.

    Note: This fixture creates a container but doesn't inject the storage
    directly since AppContainer doesn't accept storage as a parameter.
    Instead, the storage is available via async_storage_with_migrations fixture.
    """
    # AppContainer doesn't directly accept storage, so we create it normally
    # The storage can be used separately in tests
    container = AppContainer(config=app_config_with_test_db)
    return container
