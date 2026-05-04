"""
Router: Agent Collaboration Management
Provides Agent communication, task orchestration, collaboration query APIs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent_core.core.agent_manager import manager
from agent_core.collaboration.orchestrator import orchestrator
from agent_core.collaboration.agent_tools import call_agent_handler

router = APIRouter()


class CollaborationRequest(BaseModel):
    """Send collaboration message to an Agent"""
    agent_id: str
    message: str
    caller_id: Optional[str] = ""


class CollaborationResponse(BaseModel):
    """Collaboration response"""
    reply: str
    agent_id: str
    agent_name: str = ""
    success: bool = True


class DelegationRequest(BaseModel):
    """Orchestrator delegate task"""
    agent_id: str
    task: str


class SequentialDelegationRequest(BaseModel):
    """Sequential delegation of multiple tasks"""
    delegations: list[DelegationRequest]


class OrchestratorPlan(BaseModel):
    """Orchestration plan including decomposition and delegation"""
    task: str
    delegations: list[DelegationRequest]


@router.get("/collaboration/agents")
def list_collaboration_agents():
    """List all agents available for collaboration"""
    return {"agents": orchestrator.list_available_agents()}


@router.get("/collaboration/status")
def collaboration_status():
    """Get overall collaboration system status"""
    agents = orchestrator.list_available_agents()
    return {
        "agents_count": len(agents),
        "agents": agents,
    }


@router.post("/collaboration/call", response_model=CollaborationResponse)
def call_agent(req: CollaborationRequest):
    """Send collaboration request to an Agent"""
    if not req.message.strip():
        return CollaborationResponse(
            reply="Please input message content",
            agent_id=req.agent_id,
            success=False,
        )
    profile = manager.get_profile(req.agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{req.agent_id}' not found")
    try:
        reply = call_agent_handler(
            agent_id=req.agent_id,
            message=req.message,
            _manager=manager,
        )
        return CollaborationResponse(
            reply=reply,
            agent_id=req.agent_id,
            agent_name=profile.name,
            success=True,
        )
    except Exception as e:
        return CollaborationResponse(
            reply=f"Call failed: {str(e)[:200]}",
            agent_id=req.agent_id,
            agent_name=profile.name if profile else "",
            success=False,
        )


@router.post("/collaboration/delegate", response_model=CollaborationResponse)
def delegate_task(req: DelegationRequest):
    """Orchestrator delegate single task to specified Agent"""
    profile = manager.get_profile(req.agent_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Agent '{req.agent_id}' not found")
    result = orchestrator.delegate(req.agent_id, req.task)
    return CollaborationResponse(
        reply=result.result,
        agent_id=result.agent_id,
        agent_name=result.agent_name,
        success=result.success,
    )


@router.post("/collaboration/sequential")
def sequential_delegate(req: SequentialDelegationRequest):
    """Sequentially delegate multiple tasks (previous result can be referenced by next)"""
    if not req.delegations:
        return {"results": [], "summary": "No tasks to delegate"}
    delegations = [(d.agent_id, d.task) for d in req.delegations]
    results = orchestrator.sequential_delegate(delegations)
    return {"results": results, "summary": f"Completed {len(results)} tasks"}


@router.get("/collaboration/orchestrate")
def orchestrate_task(task: str):
    """Automatically decompose and orchestrate complex task"""
    plan = orchestrator.orchestrate(task)
    if not plan:
        return {"plan": None, "summary": "Task could not be orchestrated"}
    return {"plan": plan.to_dict() if hasattr(plan, 'to_dict') else str(plan)}