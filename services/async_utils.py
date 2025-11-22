from __future__ import annotations

import asyncio
from functools import partial
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def run_blocking_io(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Run a blocking I/O function in an executor to avoid blocking the event loop.

    Args:
        func: The blocking function to execute.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of the function execution.
    """
    loop = asyncio.get_running_loop()
    bound_func = partial(func, *args, **kwargs)
    result = await loop.run_in_executor(None, bound_func)
    return result


__all__ = ["run_blocking_io"]

