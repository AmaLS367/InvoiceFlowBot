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

from datetime import date  # noqa: E402
from typing import Any, Dict, List, Optional  # noqa: E402

import pytest  # noqa: E402

from config import Settings  # noqa: E402
from core.container import AppContainer  # noqa: E402
from domain.invoices import Invoice  # noqa: E402
from handlers.di_middleware import ContainerMiddleware  # noqa: E402
from storage.db_async import AsyncInvoiceStorage  # noqa: E402
from tests.fakes.fake_ocr import FakeOcr, make_fake_ocr_extractor  # noqa: E402
from tests.fakes.fake_services import FakeInvoiceService  # noqa: E402
from tests.fakes.fake_services_drafts import FakeDraftService  # noqa: E402
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


@pytest.fixture()
def handlers_container(app_config: Settings) -> AppContainer:
    """
    Create an AppContainer with fake dependencies for handler testing.

    Uses fake storage and OCR to avoid real database/API calls.
    """
    return AppContainer(
        config=app_config,
        ocr_extractor=make_fake_ocr_extractor(fake_ocr=FakeOcr()),
        save_invoice_func=make_fake_save_invoice_func(fake_storage=FakeStorage()),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage=FakeStorage()),
        load_draft_func=make_fake_load_draft_func(fake_storage=FakeStorage()),
        save_draft_func=make_fake_save_draft_func(fake_storage=FakeStorage()),
        delete_draft_func=make_fake_delete_draft_func(fake_storage=FakeStorage()),
    )


@pytest.fixture()
def handlers_data(handlers_container: AppContainer) -> Dict[str, Any]:
    """
    Create handler data dict with container for testing handlers.

    This fixture provides the data dict that handlers expect from ContainerMiddleware.
    """
    return {"container": handlers_container}


@pytest.fixture()
def fake_invoice_service(handlers_container: AppContainer) -> FakeInvoiceService:
    """
    Create a fake InvoiceService and inject it into the container.

    Returns the fake service so tests can inspect calls and configure return values.
    """
    fake_service = FakeInvoiceService()
    handlers_container.invoice_service = fake_service
    return fake_service


@pytest.fixture()
def file_handlers_container(app_config: Settings) -> AppContainer:
    """
    Create an AppContainer with fake dependencies for file handler testing.

    Uses fake storage, OCR, and draft service to avoid real database/API calls.
    """
    container = AppContainer(
        config=app_config,
        ocr_extractor=make_fake_ocr_extractor(fake_ocr=FakeOcr()),
        save_invoice_func=make_fake_save_invoice_func(fake_storage=FakeStorage()),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage=FakeStorage()),
        load_draft_func=make_fake_load_draft_func(fake_storage=FakeStorage()),
        save_draft_func=make_fake_save_draft_func(fake_storage=FakeStorage()),
        delete_draft_func=make_fake_delete_draft_func(fake_storage=FakeStorage()),
    )
    # Replace draft_service with fake
    container.draft_service = FakeDraftService()
    return container


@pytest.fixture()
def file_handlers_data(file_handlers_container: AppContainer) -> Dict[str, Any]:
    """
    Create handler data dict with container for testing file handlers.

    This fixture provides the data dict that handlers expect from ContainerMiddleware.
    """
    return {"container": file_handlers_container}


@pytest.fixture()
def integration_flow_container(
    app_config_with_test_db: Settings,
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> AppContainer:
    """
    Create an AppContainer for integration flow testing.

    Uses real AsyncInvoiceStorage with migrated database, but fake OCR.
    All services (InvoiceService, DraftService) are created with real dependencies.
    """
    # Create fake OCR
    fake_ocr = FakeOcr()

    # Create a single FakeStorage instance for drafts to ensure data persistence
    fake_draft_storage = FakeStorage()

    # Create wrapper functions for storage methods
    async def save_invoice_wrapper(invoice: Invoice, user_id: int) -> int:
        return await async_storage_with_migrations.save_invoice(invoice, user_id)

    async def fetch_invoices_wrapper(
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str],
    ) -> List[Invoice]:
        return await async_storage_with_migrations.fetch_invoices(from_date, to_date, supplier)

    # Create container with real storage but fake OCR
    container = AppContainer(
        config=app_config_with_test_db,
        ocr_extractor=make_fake_ocr_extractor(fake_ocr=fake_ocr),
        save_invoice_func=save_invoice_wrapper,
        fetch_invoices_func=fetch_invoices_wrapper,
        load_draft_func=make_fake_load_draft_func(fake_storage=fake_draft_storage),
        save_draft_func=make_fake_save_draft_func(fake_storage=fake_draft_storage),
        delete_draft_func=make_fake_delete_draft_func(fake_storage=fake_draft_storage),
    )

    return container
