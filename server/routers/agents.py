"""
Router: Custom Agent Management
Supports creating, reading, updating, and deleting custom Agents (iris cannot be deleted)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent_core.core.agent_manager import manager
from agent_core.core.agent_profile import AgentProfile, DEFAULT_AGENTS
from agent_core.core.agent_store import (
    load_agents,
    save_agents,
    generate_agent_id,
)

router = APIRouter()


class CreateAgentRequest(BaseModel):
    """Create custom Agent request"""
    name: str
    title: str = ""
    specialty: str = ""
    emoji: str = ""
    system_prompt: str = ""


class UpdateAgentRequest(BaseModel):
    """Update Agent request"""
    name: Optional[str] = None
    title: Optional[str] = None
    specialty: Optional[str] = None
    emoji: Optional[str] = None
    system_prompt: Optional[str] = None


def _get_all_agents() -> dict[str, AgentProfile]:
    """Get all Agents (merge with persistence)"""
    stored = load_agents()
    for aid, profile in manager.profiles.items():
        if aid in stored:
            # Update runtime status from manager
            if hasattr(stored[aid], 'status'):
                stored[aid].status = profile.status
        else:
            stored[aid] = profile
    return stored


def _profile_to_response(profile: AgentProfile) -> dict:
    """Convert AgentProfile to response dict"""
    status = profile.status
    if hasattr(status, 'value'):
        status = status.value
    return {
        "id": profile.id,
        "name": profile.name,
        "emoji": getattr(profile, 'emoji', ''),
        "title": getattr(profile, 'title', ''),
        "specialty": getattr(profile, 'specialty', ''),
        "status": status,
        "is_builtin": profile.id == "iris",
    }


@router.get("/agents")
def list_agents():
    """Get all Agent list"""
    agents = _get_all_agents()
    return {
        "agents": [
            _profile_to_response(p) for p in agents.values()
        ]
    }


@router.get("/agents/{agent_id}")
def get_agent(agent_id: str):
    """Get single Agent details"""
    agents = _get_all_agents()
    profile = agents.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return _profile_to_response(profile)


@router.get("/agents/{agent_id}/session")
def get_agent_session(agent_id: str):
    """Get Agent session/messages (for chat context)"""
    agents = _get_all_agents()
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    agent = manager.get_agent(agent_id)
    if not agent:
        return {"session_id": None, "messages": [], "message_count": 0}
    messages = getattr(agent, 'messages', [])
    return {
        "session_id": agent.session_id if hasattr(agent, 'session_id') else None,
        "messages": messages[-50:] if messages else [],
        "message_count": len(messages) if messages else 0,
    }


@router.post("/agents/{agent_id}/new-session")
def create_new_session(agent_id: str):
    """Create new session for Agent"""
    agents = _get_all_agents()
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    agent = manager.get_agent(agent_id)
    if agent and hasattr(agent, 'new_session'):
        agent.new_session()
    return {"success": True, "message": "New session created"}


@router.post("/agents/create")
def create_agent(req: CreateAgentRequest):
    """Create custom Agent"""
    if not req.name or not req.name.strip():
        raise HTTPException(status_code=400, detail="Agent name is required")
    name = req.name.strip()
    agent_id = generate_agent_id(name)
    if agent_id == "iris":
        raise HTTPException(status_code=400, detail="Cannot create agent with id 'iris'")
    agents = _get_all_agents()
    if agent_id in agents:
        raise HTTPException(
            status_code=409,
            detail=f"Agent with id '{agent_id}' already exists",
        )
    system_prompt = req.system_prompt or (
        f"You are '{name}', a member of the office.\n\n"
        f"## Specialty\n{req.specialty or 'General assistance'}\n\n"
        f"## Available Tools\n"
        f"- search_local_files: Search keywords in local files\n"
        f"- read_file_content: Read full content of specified file\n"
        f"- call_agent: Send message to other colleagues\n\n"
        f"## Collaboration Rules\n"
        f"- Only use call_agent when user explicitly mentions a colleague\n"
        f"- If user doesn't mention any colleague, complete tasks independently\n\n"
        f"Note: Do not use emoji symbols."
    )
    profile = AgentProfile(
        id=agent_id,
        name=name,
        system_prompt=system_prompt,
        description=req.specialty or "Office member",
    )
    agents[agent_id] = profile
    save_agents(agents)
    return {"agent": _profile_to_response(profile), "message": f"Agent '{name}' created"}


@router.put("/agents/{agent_id}")
def update_agent(agent_id: str, req: UpdateAgentRequest):
    """Update Agent configuration (iris only allows specialty and prompt modification)"""
    agents = _get_all_agents()
    profile = agents.get(agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    is_iris = agent_id == "iris"
    if is_iris:
        if req.name is not None and req.name != profile.name:
            raise HTTPException(status_code=403, detail="Cannot rename iris")
        allowed = {"specialty", "system_prompt"}
        for field, value in req.dict(exclude_unset=True).items():
            if field not in allowed:
                continue
            if value is not None:
                setattr(profile, field, value)
    else:
        if req.name is not None:
            profile.name = req.name
        if req.title is not None:
            profile.title = req.title
        if req.specialty is not None:
            profile.specialty = req.specialty
        if req.emoji is not None:
            profile.emoji = req.emoji
        if req.system_prompt is not None:
            profile.system_prompt = req.system_prompt
    agents[agent_id] = profile
    save_agents(agents)
    return {"agent": _profile_to_response(profile), "message": f"Agent '{profile.name}' updated"}


@router.delete("/agents/{agent_id}")
def delete_agent(agent_id: str):
    """Delete custom Agent (iris cannot be deleted)"""
    if agent_id == "iris":
        raise HTTPException(status_code=403, detail="Cannot delete iris (core agent)")
    agents = _get_all_agents()
    if agent_id not in agents:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    profile = agents[agent_id]
    stored = load_agents()
    stored.pop(agent_id, None)
    save_agents(stored)
    return {"message": f"Agent '{profile.name}' deleted", "agent_id": agent_id}
