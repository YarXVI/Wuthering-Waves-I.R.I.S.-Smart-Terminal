"""
Workflow Store - Workflow Persistence
Supports workflow saving, loading, deletion, and listing
"""
import json
import uuid
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import Optional
from datetime import datetime

WORKFLOW_DIR = Path(__file__).parent.parent.parent / "memory" / "workflows"


@dataclass
class WorkflowStep:
    agent_id: str
    task: str
    result: Optional[str] = None


@dataclass
class Workflow:
    id: str
    name: str
    steps: list[WorkflowStep] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> "Workflow":
        steps = [WorkflowStep(**s) for s in data.get("steps", [])]
        return Workflow(
            id=data.get("id", ""),
            name=data.get("name", ""),
            steps=steps,
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


def _ensure_storage_dir():
    """Ensure storage directory exists"""
    try:
        WORKFLOW_DIR.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError):
        return False


def _workflow_file(workflow_id: str) -> Path:
    """Get workflow file path"""
    return WORKFLOW_DIR / f"workflow_{workflow_id}.json"


def save_workflow(workflow: Workflow) -> bool:
    """Save workflow to disk"""
    if not _ensure_storage_dir():
        return False
    workflow.updated_at = datetime.now().isoformat()
    if not workflow.created_at:
        workflow.created_at = workflow.updated_at
    try:
        with open(_workflow_file(workflow.id), "w", encoding="utf-8") as f:
            json.dump(workflow.to_dict(), f, ensure_ascii=False, indent=2)
        return True
    except (OSError, IOError):
        return False


def load_workflow(workflow_id: str) -> Optional[Workflow]:
    """Load workflow from disk"""
    path = _workflow_file(workflow_id)
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Workflow.from_dict(data)
    except (OSError, IOError, json.JSONDecodeError):
        return None


def list_workflows() -> list[Workflow]:
    """List all saved workflows"""
    if not _ensure_storage_dir():
        return []
    workflows = []
    try:
        for f in WORKFLOW_DIR.glob("workflow_*.json"):
            try:
                with open(f, "r", encoding="utf-8") as fp:
                    data = json.load(fp)
                workflows.append(Workflow.from_dict(data))
            except (OSError, IOError, json.JSONDecodeError):
                continue
        workflows.sort(key=lambda w: w.updated_at or "", reverse=True)
    except OSError:
        pass
    return workflows


def delete_workflow(workflow_id: str) -> bool:
    """Delete workflow"""
    path = _workflow_file(workflow_id)
    if not path.exists():
        return False
    try:
        path.unlink()
        return True
    except OSError:
        return False


def create_workflow(name: str, steps: list[WorkflowStep]) -> Workflow:
    """Create new workflow"""
    workflow = Workflow(
        id=str(uuid.uuid4())[:8],
        name=name,
        steps=steps,
    )
    save_workflow(workflow)
    return workflow
