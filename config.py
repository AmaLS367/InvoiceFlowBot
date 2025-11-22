import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN") 
if BOT_TOKEN is None:
    raise RuntimeError("BOT_TOKEN not found or empty. Check your .env file.")

MINDEE_API_KEY = os.getenv("MINDEE_API_KEY")
if MINDEE_API_KEY is None or not MINDEE_API_KEY.strip():
    raise RuntimeError("MINDEE_API_KEY is not set. Please configure it in environment or .env file.")

MINDEE_MODEL_ID = os.getenv("MINDEE_MODEL_ID")
if MINDEE_MODEL_ID is None or not MINDEE_MODEL_ID.strip():
    raise RuntimeError("MINDEE_MODEL_ID is not set. Please configure it in environment or .env file.")

UPLOAD_FOLDER = "data/uploads"
ARTIFACTS_DIR = "data/artifacts"

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_ROTATE_MB = int(os.getenv("LOG_ROTATE_MB", "10"))
LOG_BACKUPS = int(os.getenv("LOG_BACKUPS", "5"))
LOG_CONSOLE = os.getenv("LOG_CONSOLE", "0") in ("1", "true", "True")
LOG_DIR = os.getenv("LOG_DIR")
