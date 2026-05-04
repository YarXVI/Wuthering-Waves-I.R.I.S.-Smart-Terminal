"""
Router: Skills Management
"""
from fastapi import APIRouter
from agent_core.skills_registry import skills_registry

router = APIRouter()


@router.get("/skills")
def list_skills():
    """List all registered skills"""
    skills = skills_registry.list_skills()
    return {"skills": skills, "count": len(skills)}


@router.get("/skills/{skill_id}")
def get_skill(skill_id: str):
    """Get skill details"""
    skill = skills_registry.get_skill(skill_id)
    return {"skill": skill}
