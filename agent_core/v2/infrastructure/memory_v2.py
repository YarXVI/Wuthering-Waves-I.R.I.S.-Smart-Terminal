"""
Memory System

Tiered memory storage with agent isolation and JSONL persistence.
"""
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


@dataclass
class MemoryEntry:
    """记忆条目"""
    id: str
    agent_id: str
    type: str  # note, fact, preference, summary, event
    content: str
    importance: int = 5  # 1-10
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "type": self.type,
            "content": self.content,
            "importance": self.importance,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryEntry":
        return cls(
            id=data["id"],
            agent_id=data["agent_id"],
            type=data["type"],
            content=data["content"],
            importance=data.get("importance", 5),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )


class MemoryStore:
    """
    V2 记忆存储 —— 融合 V1 和 V2 的记忆管理

    支持：
    - 按 agent 隔离存储
    - 记忆类型分类
    - 重要性评分
    - 关键词搜索
    - JSONL 持久化
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else Path.home() / ".iris" / "memory_v2"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._cache: Dict[str, List[MemoryEntry]] = {}  # agent_id -> entries

    def _agent_file(self, agent_id: str) -> Path:
        return self.storage_dir / f"{agent_id}.jsonl"

    def add(
        self,
        agent_id: str,
        content: str,
        memory_type: str = "note",
        importance: int = 5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """添加记忆"""
        with self._lock:
            entry = MemoryEntry(
                id=f"{agent_id}_{datetime.now().timestamp():.6f}",
                agent_id=agent_id,
                type=memory_type,
                content=content,
                importance=importance,
                metadata=metadata or {},
            )

            # 更新缓存
            if agent_id not in self._cache:
                self._cache[agent_id] = []
            self._cache[agent_id].append(entry)

            # 持久化
            self._append_to_disk(agent_id, entry)
            return entry

    def get(
        self,
        agent_id: str,
        memory_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[MemoryEntry]:
        """获取记忆"""
        with self._lock:
            entries = self._load_agent_entries(agent_id)

            if memory_type:
                entries = [e for e in entries if e.type == memory_type]

            # 按重要性排序，返回最重要的
            entries.sort(key=lambda e: (-e.importance, e.created_at), reverse=False)
            return entries[-limit:]

    def search(
        self,
        query: str,
        agent_id: Optional[str] = None,
        memory_type: Optional[str] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """搜索记忆"""
        with self._lock:
            query_lower = query.lower()
            results = []

            agents = [agent_id] if agent_id else self.list_agents()

            for aid in agents:
                entries = self._load_agent_entries(aid)
                for entry in entries:
                    if memory_type and entry.type != memory_type:
                        continue
                    if query_lower in entry.content.lower():
                        results.append(entry)

            # 按相关性排序（简单实现：匹配长度）
            results.sort(key=lambda e: len(query_lower) / len(e.content) if e.content else 0, reverse=True)
            return results[:limit]

    def delete(self, agent_id: str, memory_id: str) -> bool:
        """删除记忆"""
        with self._lock:
            entries = self._load_agent_entries(agent_id)
            new_entries = [e for e in entries if e.id != memory_id]

            if len(new_entries) == len(entries):
                return False

            self._cache[agent_id] = new_entries
            self._rewrite_disk(agent_id, new_entries)
            return True

    def clear(self, agent_id: str) -> int:
        """清空 agent 的所有记忆"""
        with self._lock:
            entries = self._load_agent_entries(agent_id)
            count = len(entries)

            if agent_id in self._cache:
                del self._cache[agent_id]

            file_path = self._agent_file(agent_id)
            if file_path.exists():
                file_path.unlink()

            return count

    def list_agents(self) -> List[str]:
        """列出所有有记忆的 agent"""
        agents = set()
        for f in self.storage_dir.glob("*.jsonl"):
            agents.add(f.stem)
        return sorted(agents)

    def stats(self) -> Dict[str, Any]:
        """统计信息"""
        total_entries = 0
        agents = set()
        type_count: Dict[str, int] = {}

        for f in self.storage_dir.glob("*.jsonl"):
            entries = self._read_file(f)
            total_entries += len(entries)
            if entries:
                agents.add(f.stem)
            for e in entries:
                t = e.type
                type_count[t] = type_count.get(t, 0) + 1

        return {
            "total_entries": total_entries,
            "agents": sorted(agents),
            "types": type_count,
            "storage_path": str(self.storage_dir),
        }

    def _load_agent_entries(self, agent_id: str) -> List[MemoryEntry]:
        """加载指定 agent 的所有记忆"""
        if agent_id in self._cache:
            return self._cache[agent_id]

        file_path = self._agent_file(agent_id)
        entries = self._read_file(file_path)
        self._cache[agent_id] = entries
        return entries

    def _read_file(self, file_path: Path) -> List[MemoryEntry]:
        """读取记忆文件"""
        if not file_path.exists():
            return []

        entries = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    entries.append(MemoryEntry.from_dict(data))
                except (json.JSONDecodeError, KeyError):
                    continue
        return entries

    def _append_to_disk(self, agent_id: str, entry: MemoryEntry) -> None:
        """追加单条记忆到磁盘"""
        file_path = self._agent_file(agent_id)
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

    def _rewrite_disk(self, agent_id: str, entries: List[MemoryEntry]) -> None:
        """重写整个记忆文件"""
        file_path = self._agent_file(agent_id)
        with open(file_path, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")
