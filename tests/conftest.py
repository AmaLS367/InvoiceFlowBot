import sys
from pathlib import Path

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
    return Settings()  # type: ignore[call-arg]


@pytest.fixture()
def fake_storage() -> FakeStorage:
    return FakeStorage()


@pytest.fixture()
def fake_ocr() -> FakeOcr:
    return FakeOcr()


@pytest.fixture()
def app_container(
    app_config: Settings,
    fake_storage: FakeStorage,
    fake_ocr: FakeOcr,
) -> AppContainer:
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
    return ContainerMiddleware(container=app_container)


@pytest.fixture()
def test_db_path(tmp_path: Path) -> Path:
    db_path = tmp_path / "test_db.sqlite3"
    return db_path


@pytest.fixture()
def migrated_database_url(test_db_path: Path) -> str:
    database_url = f"sqlite:///{test_db_path}"

    run_migrations_for_url(database_url)

    return database_url


@pytest.fixture()
def async_storage_with_migrations(migrated_database_url: str) -> AsyncInvoiceStorage:
    db_path = migrated_database_url.replace("sqlite:///", "")
    storage = AsyncInvoiceStorage(database_path=db_path)
    return storage


@pytest.fixture()
def app_config_with_test_db(migrated_database_url: str) -> Settings:
    config = Settings()  # type: ignore[call-arg]
    return config


@pytest.fixture()
def app_container_with_test_db(
    app_config_with_test_db: Settings,
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> AppContainer:
    container = AppContainer(config=app_config_with_test_db)
    return container


@pytest.fixture()
def handlers_container(app_config: Settings) -> AppContainer:
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
    return {"container": handlers_container}


@pytest.fixture()
def fake_invoice_service(handlers_container: AppContainer) -> FakeInvoiceService:
    fake_service = FakeInvoiceService()
    handlers_container.invoice_service = fake_service
    return fake_service


@pytest.fixture()
def file_handlers_container(app_config: Settings) -> AppContainer:
    container = AppContainer(
        config=app_config,
        ocr_extractor=make_fake_ocr_extractor(fake_ocr=FakeOcr()),
        save_invoice_func=make_fake_save_invoice_func(fake_storage=FakeStorage()),
        fetch_invoices_func=make_fake_fetch_invoices_func(fake_storage=FakeStorage()),
        load_draft_func=make_fake_load_draft_func(fake_storage=FakeStorage()),
        save_draft_func=make_fake_save_draft_func(fake_storage=FakeStorage()),
        delete_draft_func=make_fake_delete_draft_func(fake_storage=FakeStorage()),
    )
    container.draft_service = FakeDraftService()
    return container


@pytest.fixture()
def file_handlers_data(file_handlers_container: AppContainer) -> Dict[str, Any]:
    return {"container": file_handlers_container}


@pytest.fixture()
def integration_flow_container(
    app_config_with_test_db: Settings,
    async_storage_with_migrations: AsyncInvoiceStorage,
) -> AppContainer:
    fake_ocr = FakeOcr()

    fake_draft_storage = FakeStorage()

    async def save_invoice_wrapper(invoice: Invoice, user_id: int) -> int:
        return await async_storage_with_migrations.save_invoice(invoice, user_id)

    async def fetch_invoices_wrapper(
        from_date: Optional[date],
        to_date: Optional[date],
        supplier: Optional[str],
    ) -> List[Invoice]:
        return await async_storage_with_migrations.fetch_invoices(from_date, to_date, supplier)

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
