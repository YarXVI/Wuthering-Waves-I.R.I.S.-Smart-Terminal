"""
Memory Indexer - Index memories for fast retrieval
"""

from typing import List, Dict, Any


class MemoryIndexer:
    """Indexes memories for fast retrieval"""

    def __init__(self):
        self.index: Dict[str, List[float]] = {}

    def add(self, memory_id: str, embedding: List[float]):
        """Add memory to index"""
        self.index[memory_id] = embedding

    def search(self, query_embedding: List[float], top_k: int = 5) -> List[str]:
        """Search index for similar memories"""
        return list(self.index.keys())[:top_k]

    def remove(self, memory_id: str):
        """Remove memory from index"""
        self.index.pop(memory_id, None)


indexer = MemoryIndexer()
