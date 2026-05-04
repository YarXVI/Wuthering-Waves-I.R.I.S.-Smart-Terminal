"""
Async Utilities - Helper functions for async operations
"""

import asyncio
from typing import Callable, Any


def fire_and_forget(coro):
    """
    Safely trigger an async task (fire-and-forget)
    Uses create_task when event loop is available, else run() in a new thread
    """
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        asyncio.run(coro)


async def run_with_timeout(coro, timeout: float):
    """Run coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return None


def async_to_sync(func: Callable) -> Callable:
    """Decorator to run async function synchronously"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper
