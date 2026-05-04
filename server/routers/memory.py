"""
Router: Memory Management (memory_store + session_store)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from agent_core.memory.memory_store import (
    add_memory, get_memories, search_memories,
    delete_memory, clear_memories, stats,
)

router = APIRouter()


class MemoryRequest(BaseModel):
    """Add memory request"""
    agent_id: str
    content: str
    type: str = "note"
    metadata: dict = {}


class MemoryResponse(BaseModel):
    """Memory response"""
    id: str
    agent_id: str
    type: str
    content: str
    metadata: dict
    created_at: str


@router.get("/memories/stats")
def memory_system_stats():
    """Get global memory system statistics"""
    return stats()


@router.get("/memories/{agent_id}")
def list_memories(agent_id: str, type: str = "", limit: int = 50):
    """Get memory entries for specified Agent"""
    mem_type = type if type else None
    return {"agent_id": agent_id, "memories": get_memories(agent_id, mem_type, limit)}


@router.post("/memories")
def create_memory(req: MemoryRequest):
    """Add a memory entry"""
    entry = add_memory(req.agent_id, req.content, req.type, req.metadata)
    return MemoryResponse(**entry)


@router.get("/memories/search/{query}")
def search_memory_entries(query: str, type: str = ""):
    """Search all memories"""
    mem_type = type if type else None
    return {"query": query, "results": search_memories(query, mem_type)}


@router.delete("/memories/{agent_id}/{memory_id}")
def remove_memory(agent_id: str, memory_id: str):
    """Delete specified memory entry"""
    ok = delete_memory(agent_id, memory_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Memory not found")
    return {"status": "deleted"}


@router.delete("/memories/{agent_id}")
def clear_agent_memories(agent_id: str):
    """Clear all memories for specified Agent"""
    count = clear_memories(agent_id)
    return {"status": "cleared", "deleted": count}


@router.get("/usage/stats")
def api_usage_stats(days: int = 7):
    """Get API usage statistics for last N days"""
    from agent_core.memory.usage_stats import get_daily_usage, get_recent_days
    if days == 1:
        return get_daily_usage()
    return {"days": get_recent_days(days)}