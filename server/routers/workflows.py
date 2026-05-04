"""
Router: Workflow Management
Provides workflow creation, saving, loading, deletion and execution APIs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from agent_core.workflow.workflow_store import (
    Workflow, WorkflowStep, save_workflow, load_workflow,
    list_workflows, delete_workflow, create_workflow
)
from agent_core.core.agent_manager import manager
from agent_core.collaboration.agent_tools import call_agent_handler

router = APIRouter()


class WorkflowStepRequest(BaseModel):
    """Workflow step request"""
    agent_id: str
    task: str
    result: Optional[str] = None


class WorkflowSaveRequest(BaseModel):
    """Save workflow request"""
    id: Optional[str] = None
    name: str
    steps: list[WorkflowStepRequest]


class WorkflowExecuteRequest(BaseModel):
    """Execute workflow request"""
    steps: list[WorkflowStepRequest]


@router.get("/workflows")
def get_workflows():
    """List all saved workflows"""
    workflows = list_workflows()
    return {
        "workflows": [
            {
                "id": w.id,
                "name": w.name,
                "step_count": len(w.steps),
                "created_at": w.created_at,
                "updated_at": w.updated_at,
            }
            for w in workflows
        ]
    }


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    """Get specified workflow details"""
    workflow = load_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"workflow": workflow.to_dict()}


@router.post("/workflows")
def create_or_save_workflow(req: WorkflowSaveRequest):
    """Create or save workflow"""
    steps = [WorkflowStep(**s.model_dump()) for s in req.steps]
    if req.id:
        workflow = load_workflow(req.id)
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        workflow.name = req.name
        workflow.steps = steps
    else:
        workflow = create_workflow(req.name, steps)
    save_workflow(workflow)
    return {"workflow": workflow.to_dict()}


@router.delete("/workflows/{workflow_id}")
def remove_workflow(workflow_id: str):
    """Delete workflow"""
    success = delete_workflow(workflow_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"success": True}


@router.post("/workflows/execute")
def execute_workflow(req: WorkflowExecuteRequest):
    """Execute workflow steps"""
    results = []
    for step in req.steps:
        try:
            reply = call_agent_handler(
                agent_id=step.agent_id,
                message=step.task,
                _manager=manager,
            )
            results.append({
                "agent_id": step.agent_id,
                "task": step.task,
                "result": reply,
                "success": True,
            })
        except Exception as e:
            results.append({
                "agent_id": step.agent_id,
                "task": step.task,
                "result": f"Error: {str(e)[:200]}",
                "success": False,
            })
    return {"results": results}