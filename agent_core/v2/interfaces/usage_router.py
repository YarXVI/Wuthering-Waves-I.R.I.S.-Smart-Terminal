"""
Router: Usage & Conversation History

Usage tracking and conversation history endpoints.
"""
from fastapi import APIRouter
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, List

from agent_core.v2.infrastructure.memory_manager import MemoryManager

router = APIRouter(prefix="/usage", tags=["usage"])


def get_manager() -> MemoryManager:
    """获取记忆管理器"""
    return MemoryManager()


def _generate_mock_stats(days: int) -> List[Dict[str, Any]]:
    """生成模拟用量统计（实际应从持久化存储读取）"""
    stats = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        stats.append({
            "date": date,
            "total_tokens": 0,
            "total_cost": 0.0,
            "total_requests": 0,
            "by_agent": {},
        })
    return stats


@router.get("/daily")
def daily_usage(days: int = 7):
    """获取每日用量统计"""
    stats = _generate_mock_stats(days)
    summary = {
        "total_tokens": sum(s["total_tokens"] for s in stats),
        "total_cost": round(sum(s["total_cost"] for s in stats), 6),
        "total_requests": sum(s["total_requests"] for s in stats),
    }
    return {"summary": summary, "daily": stats}


@router.get("/by-model")
def usage_by_model(days: int = 7):
    """按模型统计用量"""
    result = {}
    stats = _generate_mock_stats(days)
    for stat in stats:
        for agent, data in stat.get("by_agent", {}).items():
            if agent not in result:
                result[agent] = {"requests": 0, "tokens": 0}
            result[agent]["requests"] += data.get("requests", 0)
            result[agent]["tokens"] += data.get("total_tokens", 0)
    return {"by_model": result}


@router.get("/conversations/history")
async def conversation_history(agent_id: str = "", limit: int = 50):
    """获取对话历史"""
    manager = get_manager()

    sessions = []
    if agent_id:
        memory = await manager.load(agent_id)
        messages = memory.short_term or []
        sessions.append({
            "agent_id": agent_id,
            "message_count": len(messages),
            "messages": messages[-limit:] if messages else [],
        })
        return {"sessions": sessions}

    # 扫描所有 agent 的记忆文件
    memory_dir = Path.home() / ".iris" / "memory"
    if memory_dir.exists():
        files = sorted(memory_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)[:10]
        for f in files:
            aid = f.stem
            memory = await manager.load(aid)
            msgs = memory.short_term or []
            sessions.append({
                "agent_id": aid,
                "message_count": len(msgs),
                "messages": msgs[-min(limit, 30):] if msgs else [],
            })

    return {"sessions": sessions}


@router.get("/conversations/summary")
async def conversation_summary():
    """获取对话摘要"""
    manager = get_manager()
    result = []

    memory_dir = Path.home() / ".iris" / "memory"
    if memory_dir.exists():
        files = sorted(memory_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True)[:20]
        for f in files:
            aid = f.stem
            memory = await manager.load(aid)
            msgs = memory.short_term or []
            first_msg = msgs[0].get("content", "")[:80] if msgs else ""
            last_msg = msgs[-1].get("content", "")[:80] if msgs else ""
            result.append({
                "agent_id": aid,
                "message_count": len(msgs),
                "first_message": first_msg,
                "last_message": last_msg,
            })

    return {"conversations": result}
