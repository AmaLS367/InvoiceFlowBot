from __future__ import annotations

from typing import Any, Dict, Optional

from aiogram.fsm.state import State


class FakeFSMContext:
    """Fake FSM context for testing."""

    def __init__(self) -> None:
        self._state: Optional[State] = None
        self._data: Dict[str, Any] = {}

    async def get_state(self) -> Optional[State]:
        return self._state

    async def set_state(self, state: State) -> None:
        self._state = state

    async def update_data(self, data: Dict[str, Any]) -> None:
        self._data.update(data)

    async def get_data(self) -> Dict[str, Any]:
        return self._data.copy()

    async def clear(self) -> None:
        self._state = None
        self._data = {}

