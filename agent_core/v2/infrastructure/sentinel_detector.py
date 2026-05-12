"""
Sentinel Detector

Detects sentinel markers like [NEED_CHUNK:xxx] in model output to trigger chunk loading.
"""
import re
from typing import List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class LoadRequest:
    """加载请求"""
    chunk_id: str
    raw_marker: str
    position: int
    confidence: float = 1.0


class SentinelDetector:
    """V2 原生哨兵检测器"""

    PATTERNS = [
        re.compile(r"\[NEED_CHUNK:([A-Za-z0-9_\-]+)\]"),
        re.compile(r"\[LOAD_CHUNK:([A-Za-z0-9_\-]+)\]"),
        re.compile(r"\[FETCH:([A-Za-z0-9_\-]+)\]"),
    ]

    def __init__(self):
        self._buffer = ""
        self._clean_buffer = ""
        self._requests: List[LoadRequest] = []

    def reset(self) -> None:
        """重置检测器状态"""
        self._buffer = ""
        self._clean_buffer = ""
        self._requests = []

    def feed(self, text: str) -> List[LoadRequest]:
        """消费文本流，检测哨兵标记"""
        self._buffer += text
        self._clean_buffer += text

        requests = []
        for pattern in self.PATTERNS:
            for match in pattern.finditer(self._buffer):
                chunk_id = match.group(1)
                raw = match.group(0)
                pos = match.start()

                # 去重
                if any(r.chunk_id == chunk_id for r in self._requests):
                    continue

                req = LoadRequest(
                    chunk_id=chunk_id,
                    raw_marker=raw,
                    position=pos,
                )
                requests.append(req)
                self._requests.append(req)

                # 从 clean_buffer 中移除哨兵标记
                self._clean_buffer = self._clean_buffer.replace(raw, "")

        return requests

    def get_clean_buffer(self) -> str:
        """获取已清理哨兵标记的文本"""
        return self._clean_buffer.strip()

    def has_pending_requests(self) -> bool:
        """是否有待处理的加载请求"""
        return len(self._requests) > 0

    def get_requests(self) -> List[LoadRequest]:
        """获取所有检测到的加载请求"""
        return list(self._requests)
