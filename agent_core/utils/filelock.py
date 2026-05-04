"""
File lock utilities for concurrent file access
"""

import os
import time
import json
from pathlib import Path
from typing import Optional, Any


class FileLock:
    """Simple file lock compatible with Windows and Unix"""

    def __init__(self, lock_file: Path, timeout: float = 10.0):
        self.lock_file = lock_file
        self.timeout = timeout
        self._locked = False

    def acquire(self, blocking: bool = True) -> bool:
        """Acquire the lock"""
        start_time = time.time()

        while True:
            try:
                if self.lock_file.exists():
                    if blocking:
                        time.sleep(0.1)
                        if time.time() - start_time >= self.timeout:
                            return False
                        continue
                    else:
                        return False
                else:
                    self.lock_file.touch()
                    self._locked = True
                    return True
            except Exception:
                if blocking:
                    time.sleep(0.1)
                    if time.time() - start_time >= self.timeout:
                        return False
                else:
                    return False

    def release(self):
        """Release the lock"""
        if self._locked:
            try:
                if self.lock_file.exists():
                    self.lock_file.unlink()
            except:
                pass
            self._locked = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


class TimeoutLock:
    """Lock with timeout support"""

    def __init__(self, resource_id: str, timeout: float = 10.0):
        self.resource_id = resource_id
        self.timeout = timeout
        self._locked = False
        self._lock_dir = Path.home() / ".iris" / "locks"
        self._lock_dir.mkdir(parents=True, exist_ok=True)

    def acquire(self) -> bool:
        """Acquire the lock"""
        lock_file = self._lock_dir / f"{self.resource_id}.lock"
        lock = FileLock(lock_file, self.timeout)
        self._locked = lock.acquire()
        return self._locked

    def release(self):
        """Release the lock"""
        if self._locked:
            lock_file = self._lock_dir / f"{self.resource_id}.lock"
            lock = FileLock(lock_file, 1.0)
            lock.release()
            self._locked = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
        return False


def locked_write(filepath: Path, data: Any, mode: str = 'w') -> bool:
    """Write data to file with locking"""
    lock_file = Path(str(filepath) + '.lock')
    lock = FileLock(lock_file, timeout=5.0)

    if not lock.acquire():
        return False

    try:
        if mode == 'w':
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(data, (dict, list)):
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    f.write(str(data))
        elif mode == 'wb':
            with open(filepath, 'wb') as f:
                f.write(data)
        return True
    except Exception:
        return False
    finally:
        lock.release()


def locked_read(filepath: Path) -> Optional[str]:
    """Read file content with locking"""
    lock_file = Path(str(filepath) + '.lock')
    lock = FileLock(lock_file, timeout=5.0)

    if not lock.acquire():
        return None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None
    finally:
        lock.release()
