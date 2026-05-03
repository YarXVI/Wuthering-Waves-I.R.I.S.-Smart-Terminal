"""
隔离工具 �?模块隔离加载的通用模式
"""

import importlib
import traceback


def safe_import(module_path: str):
    """
    安全导入模块，失败时返回 None 而不是炸掉整个应用�?

    用法:
        mcp_module = safe_import("agent_core.mcp.mcp_client")
        if mcp_module:
            mcp_module.do_something()
    """
    try:
        return importlib.import_module(module_path)
    except Exception as e:
        print(f"[SafeImport] Failed to load '{module_path}': {e}")
        traceback.print_exc(limit=2)
        return None


def safe_call(func, default=None, *args, **kwargs):
    """
    安全调用函数，捕获所有异常�?

    用法:
        result = safe_call(mcp_manager.get_all_tools, default=[])
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[SafeCall] {getattr(func, '__name__', '?')} failed: {e}")
        traceback.print_exc(limit=2)
        return default


def safe_getattr(obj, attr, default=None):
    """安全获取属�?""
    try:
        return getattr(obj, attr, default)
    except Exception:
        return default
