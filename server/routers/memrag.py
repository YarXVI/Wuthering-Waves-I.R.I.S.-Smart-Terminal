"""
路由：MemRAG 记忆增强
"""

from fastapi import APIRouter
from pydantic import BaseModel
from agent_core.memrag.config import memrag_config
from agent_core.memrag.pipeline import pipeline
from agent_core.memrag.memory_indexer import indexer

router = APIRouter()


class MemRAGToggleRequest(BaseModel):
    enabled: bool


@router.get("/memrag")
def get_memrag_status():
    """获取 MemRAG 当前状�?""
    return {
        "enabled": memrag_config.enabled,
        "top_k": memrag_config.top_k,
        "embedding_available": pipeline.embedding_available,
        "index_size": indexer.size,
        "stats": {
            "retrievals": memrag_config.total_retrievals,
            "injections": memrag_config.total_injections,
        },
    }


@router.post("/memrag/toggle")
def toggle_memrag(req: MemRAGToggleRequest):
    """切换 MemRAG 记忆增强开�?""
    was = memrag_config.enabled
    memrag_config.enabled = req.enabled
    return {
        "status": "ok",
        "previous": was,
        "current": memrag_config.enabled,
    }


@router.get("/memrag/index/{agent_id}")
def get_memrag_index(agent_id: str):
    """查看指定 Agent 的向量索引内�?""
    entries = [e for e in indexer._entries if e["agent_id"] == agent_id]
    return {
        "agent_id": agent_id,
        "total": len(entries),
        "entries": [
            {"id": e["id"], "type": e["type"], "text_preview": e["text"][:100],
             "has_vector": len(e.get("vector", [])) > 0}
            for e in entries
        ],
    }
