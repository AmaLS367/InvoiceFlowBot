"""
Pytest configuration for all tests.
"""
import os
import sys
from pathlib import Path

# Add project root to Python path for imports (executed at module import time)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set default environment variables for tests (executed at module import time)
os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("MINDEE_API_KEY", "test-api-key")
os.environ.setdefault("MINDEE_MODEL_ID", "test-model-id")


def pytest_configure(config):
    """
    Ensure project root is in sys.path before any test imports.
    This hook runs early in the pytest lifecycle.
    """
    import sys
    from pathlib import Path
    import os
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    # Set default environment variables for tests
    os.environ.setdefault("BOT_TOKEN", "test-token")
    os.environ.setdefault("MINDEE_API_KEY", "test-api-key")
    os.environ.setdefault("MINDEE_MODEL_ID", "test-model-id")


def pytest_sessionstart(session):
    """
    Called after the Session object has been created and before performing collection.
    This runs even earlier than pytest_configure.
    """
    import sys
    from pathlib import Path
    import os
    
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    # Set default environment variables for tests
    os.environ.setdefault("BOT_TOKEN", "test-token")
    os.environ.setdefault("MINDEE_API_KEY", "test-api-key")
    os.environ.setdefault("MINDEE_MODEL_ID", "test-model-id")

