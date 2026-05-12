"""FastAPI router for Agent v2 API."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agent_core.v2.application.agent_service import AgentService


router = APIRouter(prefix="/v2/agents", tags=["Agent V2"])

# Global service instance (to be initialized properly in production)
_agent_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Get or create the agent service."""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service


class ChatRequest(BaseModel):
    agent_id: str = Field(..., description="Agent identifier")
    message: str = Field(..., description="User message")
    user_id: str = Field(default="default", description="User identifier")
    room_id: Optional[str] = Field(default=None, description="Room identifier")


class ChatResponse(BaseModel):
    content: str
    reasoning: str = ""
    steps_taken: int = 0
    tool_calls: int = 0
    skills_used: list[str] = []
    skills_distilled: list[str] = []
    is_success: bool = True
    error: Optional[str] = None


class AgentRegisterRequest(BaseModel):
    agent_id: str
    name: str
    model: str = "gpt-4o"
    description: Optional[str] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with an agent."""
    try:
        service = get_agent_service()
        result = await service.chat(
            agent_id=request.agent_id,
            user_message=request.message,
            user_id=request.user_id,
            room_id=request.room_id,
        )
        return ChatResponse(
            content=result.content,
            reasoning=result.reasoning,
            steps_taken=result.steps_taken,
            tool_calls=len(result.tool_calls),
            skills_used=result.skills_used,
            skills_distilled=result.skills_distilled,
            is_success=result.is_success,
            error=result.error,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/register")
async def register_agent(request: AgentRegisterRequest):
    """Register a new agent."""
    service = get_agent_service()
    service.register_agent(request.agent_id, {
        "name": request.name,
        "model": request.model,
        "description": request.description,
    })
    return {"status": "ok", "agent_id": request.agent_id}


@router.get("/list")
async def list_agents():
    """List all registered agents."""
    service = get_agent_service()
    return {"agents": service.list_agents()}


@router.get("/{agent_id}/memory")
async def get_memory(agent_id: str, user_id: str = "default"):
    """Get agent memory context."""
    service = get_agent_service()
    memory = await service.get_memory(agent_id, user_id)
    return memory
