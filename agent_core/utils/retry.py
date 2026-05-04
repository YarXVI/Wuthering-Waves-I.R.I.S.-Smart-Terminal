"""
Retry Utilities - Provides configurable retry mechanism
"""

import time
import asyncio
from typing import Callable, Any, Type, Tuple


class RetryConfig:
    """Retry configuration"""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 10.0,
        backoff_factor: float = 2.0,
        retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.retry_on_exceptions = retry_on_exceptions


def retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Decorator: Add retry mechanism to function

    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        retry_on_exceptions: Exception types that trigger retry

    Example:
        @retry(max_retries=3, base_delay=1.0)
        def call_api():
            # Operation that may fail
            return requests.get(url)
    """
    config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        retry_on_exceptions=retry_on_exceptions,
    )

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = base_delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retry_on_exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)

            raise last_exception

        return wrapper

    return decorator


def async_retry(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    retry_on_exceptions: Tuple[Type[Exception], ...] = (Exception,),
):
    """
    Async decorator: Add retry mechanism to async function

    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        retry_on_exceptions: Exception types that trigger retry

    Example:
        @async_retry(max_retries=3, base_delay=1.0)
        async def call_api():
            # Async operation that may fail
            return await asyncio.sleep(1)
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            delay = base_delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except retry_on_exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                        delay = min(delay * backoff_factor, max_delay)

            raise last_exception

        return wrapper

    return decorator
