"""
Isolation utilities for safe module loading
Prevents entire application from crashing due to single module errors
"""

import sys
import traceback
from typing import Any, Callable, Optional


def safe_import(module_name: str) -> Optional[Any]:
    """
    Safely import a module, returning None on failure instead of crashing
    """
    if module_name in sys.modules:
        return sys.modules[module_name]

    try:
        __import__(module_name)
        return sys.modules.get(module_name)
    except Exception:
        return None


def safe_call(func: Callable, default: Any = None, *args, **kwargs) -> Any:
    """
    Safely call a function, returning default on failure instead of crashing
    """
    try:
        return func(*args, **kwargs)
    except Exception:
        return default


def safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    """
    Safely get an attribute, returning default on failure
    """
    try:
        return getattr(obj, name, default)
    except Exception:
        return default


def safe_setattr(obj: Any, name: str, value: Any) -> bool:
    """
    Safely set an attribute, returning True on success
    """
    try:
        setattr(obj, name, value)
        return True
    except Exception:
        return False


class IsolationContext:
    """Context manager for isolated operations"""

    def __init__(self, operation_name: str = "operation"):
        self.operation_name = operation_name
        self.error: Optional[Exception] = None
        self.traceback_str: Optional[str] = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            self.traceback_str = ''.join(traceback.format_exception(exc_type, exc_val, exc_tb))
            print(f"[ISOLATION] {self.operation_name} failed: {exc_val}")
            return True  # Suppress the exception
        return False
