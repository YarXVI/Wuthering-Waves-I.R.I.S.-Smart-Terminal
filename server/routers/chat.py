"""
Router: Chat & Agent Management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent_core.core.agent_manager import manager
from agent_core.core.agent_profile import AgentProfile
from agent_core.core.agent_store import load_agents, save_agents
from agent_core.config import config
from agent_core.memrag.config import memrag_config
from agent_core.memrag.pipeline import pipeline

router = APIRouter()


class ChatRequest(BaseModel):
    """Chat request"""
    message: str
    agent_id: str = "iris"


class ChatResponse(BaseModel):
    """Chat response"""
    response: str
    agent_id: str
    tool_calls: Optional[list] = None


class StreamChatRequest(BaseModel):
    """Streaming chat request"""
    message: str
    agent_id: str = "iris"


@router.post("/chat/stream")
async def stream_chat(req: StreamChatRequest):
    """Streaming chat endpoint"""
    raise HTTPException(status_code=501, detail="Streaming not implemented")


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Send message and get response"""
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is required")
    if not req.agent_id:
        req.agent_id = "iris"
    profile = manager.profiles.get(req.agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{req.agent_id}' not found")
    try:
        agent = manager.get_agent(req.agent_id)
        if agent:
            response = agent.chat(req.message)
            return ChatResponse(
                response=response or "No response",
                agent_id=req.agent_id,
                tool_calls=None,
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to get agent instance")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@router.get("/chat/history/{agent_id}")
def get_chat_history(agent_id: str, limit: int = 50):
    """Get chat history for agent"""
    profile = manager.profiles.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    agent = manager.get_agent(agent_id)
    if agent:
        history = getattr(agent, 'history', [])
        return {
            "agent_id": agent_id,
            "messages": history[-limit:] if history else [],
            "total": len(history) if history else 0,
        }
    return {
        "agent_id": agent_id,
        "messages": [],
        "total": 0,
    }


@router.delete("/chat/history/{agent_id}")
def clear_chat_history(agent_id: str):
    """Clear chat history for agent"""
    if agent_id == "iris":
        raise HTTPException(status_code=403, detail="Cannot clear iris history")
    profile = manager.profiles.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    agent = manager.get_agent(agent_id)
    if agent and hasattr(agent, 'history'):
        agent.history = []
    return {"message": f"History cleared for agent '{agent_id}'"}


@router.post("/chat/reset/{agent_id}")
def reset_chat(agent_id: str):
    """Reset agent session"""
    if agent_id == "iris":
        raise HTTPException(status_code=403, detail="Cannot reset iris session")
    profile = manager.profiles.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    agent = manager.get_agent(agent_id)
    if agent and hasattr(agent, 'history'):
        agent.history = []
    return {"message": f"Agent '{agent_id}' session reset"}
