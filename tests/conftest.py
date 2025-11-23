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
from tests.fakes.fake_ocr import FakeOcr, make_fake_ocr_extractor  # noqa: E402
from tests.fakes.fake_storage import (  # noqa: E402
    FakeStorage,
    make_fake_delete_draft_func,
    make_fake_fetch_invoices_func,
    make_fake_load_draft_func,
    make_fake_save_draft_func,
    make_fake_save_invoice_func,
)


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
