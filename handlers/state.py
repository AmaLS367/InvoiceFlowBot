from typing import Any, Dict

# Global state dictionaries for user sessions
PENDING_EDIT: Dict[int, Dict[str, Any]] = {}
PENDING_PERIOD: Dict[int, Dict[str, Any]] = {}