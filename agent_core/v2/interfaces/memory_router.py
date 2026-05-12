"""
Router: Memory API

Memory management endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from agent_core.v2.infrastructure.memory_manager import MemoryManager

router = APIRouter(prefix="/memory", tags=["memory"])


def get_manager() -> MemoryManager:
    """获取记忆管理器"""
    return MemoryManager()


class MemoryRequest(BaseModel):
    """添加记忆请求"""
    agent_id: str
    content: str
    role: str = "user"
    metadata: dict = {}


class MemorySearchRequest(BaseModel):
    """搜索记忆请求"""
    agent_id: str
    query: str
    memory_type: Optional[str] = None
    limit: int = 10


@router.get("/{agent_id}")
async def load_memory(agent_id: str):
    """加载指定 Agent 的记忆"""
    manager = get_manager()
    memory = await manager.load(agent_id)

    return {
        "agent_id": agent_id,
        "working": memory.working,
        "short_term": memory.short_term,
        "long_term_count": len(memory.long_term) if memory.long_term else 0,
        "user_profile": memory.user_profile,
    }


@router.post("/{agent_id}/save")
async def save_message(agent_id: str, req: MemoryRequest):
    """保存消息到记忆"""
    manager = get_manager()
    await manager.save_message(
        agent_id,
        {"role": req.role, "content": req.content, **req.metadata},
    )

    return {
        "success": True,
        "agent_id": agent_id,
        "role": req.role,
        "content_preview": req.content[:100] if len(req.content) > 100 else req.content,
    }


@router.post("/{agent_id}/working")
async def update_working_memory(agent_id: str, content: str):
    """更新工作记忆"""
    manager = get_manager()
    await manager.update_working_memory(agent_id, content)

    return {
        "success": True,
        "agent_id": agent_id,
        "working_memory": content,
    }


@router.post("/{agent_id}/profile")
async def update_user_profile(agent_id: str, profile: Dict[str, Any]):
    """更新用户画像"""
    manager = get_manager()
    await manager.update_user_profile(agent_id, profile)

    return {
        "success": True,
        "agent_id": agent_id,
        "profile": profile,
    }


@router.post("/search")
async def search_memories(req: MemorySearchRequest):
    """搜索记忆"""
    manager = get_manager()
    results = await manager.search(
        req.agent_id,
        req.query,
        memory_type=req.memory_type,
        limit=req.limit,
    )

    return {
        "agent_id": req.agent_id,
        "query": req.query,
        "results": results,
        "count": len(results),
    }


@router.delete("/{agent_id}")
async def clear_memory(agent_id: str):
    """清除指定 Agent 的所有记忆"""
    manager = get_manager()
    await manager.clear(agent_id)

    return {
        "success": True,
        "agent_id": agent_id,
        "message": "Memory cleared",
    }


@router.get("/{agent_id}/stats")
async def memory_stats(agent_id: str):
    """获取记忆统计"""
    manager = get_manager()
    stats = await manager.get_stats(agent_id)

    return {
        "agent_id": agent_id,
        "stats": stats,
    }
