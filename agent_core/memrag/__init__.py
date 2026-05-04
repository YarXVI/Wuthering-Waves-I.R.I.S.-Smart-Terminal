"""
MemRAG - Lightweight memory-enhanced RAG module
Provides semantic memory retrieval and context injection for multi-Agent systems
"""

from agent_core.memrag.config import memrag_config
from agent_core.memrag.pipeline import MemRAGPipeline

__all__ = ["memrag_config", "MemRAGPipeline"]
