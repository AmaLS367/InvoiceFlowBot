"""
Pytest configuration for all tests.
"""
import os

os.environ.setdefault("BOT_TOKEN", "test-token")
os.environ.setdefault("MINDEE_API_KEY", "test-api-key")
os.environ.setdefault("MINDEE_MODEL_ID", "test-model-id")
