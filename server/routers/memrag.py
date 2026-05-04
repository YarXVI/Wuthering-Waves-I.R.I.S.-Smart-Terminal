"""
Router: MemRAG Memory Enhancement
"""
from fastapi import APIRouter
from pydantic import BaseModel
from agent_core.memrag.config import memrag_config
from agent_core.memrag.pipeline import pipeline
from agent_core.memrag.memory_indexer import indexer

router = APIRouter()


class MemRAGToggleRequest(BaseModel):
    """Toggle MemRAG request"""
    enabled: bool


@router.get("/memrag")
def get_memrag_status():
    """Get current MemRAG status"""
    index_size = len(indexer._entries) if hasattr(indexer, '_entries') else 0
    return {
        "enabled": memrag_config.enabled,
        "top_k": memrag_config.top_k,
        "embedding_available": pipeline.embedding_available,
        "index_size": index_size,
        "stats": {
            "retrievals": memrag_config.total_retrievals,
            "injections": memrag_config.total_injections,
        },
    }


@router.post("/memrag/toggle")
def toggle_memrag(req: MemRAGToggleRequest):
    """Toggle MemRAG memory enhancement on/off"""
    was = memrag_config.enabled
    memrag_config.enabled = req.enabled
    return {
        "status": "ok",
        "previous": was,
        "current": memrag_config.enabled,
    }


@router.get("/memrag/index/{agent_id}")
def get_memrag_index(agent_id: str):
    """View vector index content for specified Agent"""
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
