"""
文件锁和存储并发测试
"""
import sys
import os
import json
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agent_core.utils.filelock import FileLock, locked_write, locked_read


class TestFileLock:
    """文件锁并发安全测�?""

    def test_lock_acquire_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            lock = FileLock(str(path))
            assert lock.acquire() is True
            lock.release()

    def test_lock_mutual_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            lock1 = FileLock(str(path), timeout=1.0)
            lock2 = FileLock(str(path), timeout=1.0)

            assert lock1.acquire() is True
            assert lock2.acquire() is False  # 无法同时获取
            lock1.release()
            assert lock2.acquire() is True
            lock2.release()

    def test_locked_write_and_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            data = '{"key": "value"}'

            assert locked_write(str(path), data) is True
            result = locked_read(str(path))
            assert result is not None
            assert json.loads(result) == {"key": "value"}

    def test_locked_write_atomic(self):
        """验证原子写入 �?临时文件方式"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "test.json"
            path.write_text("original", encoding="utf-8")

            # 在写之前检查临时文件是否存�?            tmp_path = path.with_suffix(".tmp")
            assert locked_write(str(path), '{"new": "data"}') is True
            assert not tmp_path.exists()  # 临时文件应已被清�?            assert path.read_text(encoding="utf-8") == '{"new": "data"}'


if __name__ == "__main__":
    pytest.main(["-v", __file__])
