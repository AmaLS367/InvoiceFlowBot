from typing import Dict, Any

# Global state dictionaries for user sessions
CURRENT_PARSE: Dict[int, Dict[str, Any]] = {}
PENDING_EDIT: Dict[int, Dict[str, Any]] = {}
PENDING_PERIOD: Dict[int, Dict[str, Any]] = {}