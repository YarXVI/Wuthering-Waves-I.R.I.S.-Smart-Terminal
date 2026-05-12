"""
Router: Skills API

Skill management and execution endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from agent_core.v2.infrastructure.skill_engine import (
    SkillEngine, Skill, SkillInfo, SkillLevel,
    get_skill_engine, get_level_definition
)

router = APIRouter(prefix="/skills", tags=["skills"])


def get_engine() -> SkillEngine:
    """获取技能引擎"""
    return get_skill_engine()


@router.get("/list")
async def list_skills(tag: Optional[str] = None):
    """列出所有技能"""
    engine = get_engine()
    skills = await engine.list_skills(tag=tag)

    return {
        "skills": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "level": s.level,
                "tags": s.tags,
                "usage_count": s.usage_count,
            }
            for s in skills
        ],
        "count": len(skills),
    }


@router.get("/info/list")
async def list_skill_infos():
    """列出所有技能信息（V1兼容）"""
    engine = get_engine()
    infos = engine.get_all_skill_infos()

    return {
        "skills": [s.to_dict() for s in infos],
        "count": len(infos),
    }


@router.get("/stats")
async def get_skill_stats():
    """获取技能统计信息"""
    engine = get_engine()
    stats = engine.get_stats()

    return stats


@router.get("/levels")
async def list_skill_levels():
    """列出所有技能等级定义"""
    from agent_core.v2 import get_all_level_definitions

    defs = get_all_level_definitions()
    return {
        "levels": [d.to_dict() for d in defs],
    }


@router.get("/recommend")
async def recommend_skills(
    context: str,
    trust_level: float = 0.0,
    usage_count: int = 0,
    limit: int = 5,
):
    """根据上下文推荐技能"""
    engine = get_engine()
    engine.build_index()
    recommendations = engine.recommend(
        context=context,
        trust_level=trust_level,
        usage_count=usage_count,
        limit=limit,
    )

    return {
        "recommendations": [r.to_dict() for r in recommendations],
        "count": len(recommendations),
    }


@router.get("/{skill_id}")
async def get_skill(skill_id: str):
    """获取技能详情"""
    engine = get_engine()
    skill = await engine.load(skill_id)

    if not skill:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

    return {
        "id": skill.id,
        "name": skill.name,
        "description": skill.description,
        "level": skill.level,
        "parameters": skill.parameters,
        "prompt_template": skill.prompt_template,
        "tags": skill.tags,
        "usage_count": skill.usage_count,
        "created_at": skill.created_at.isoformat(),
    }


@router.get("/{skill_id}/info")
async def get_skill_info(skill_id: str):
    """获取技能信息（V1兼容）"""
    engine = get_engine()
    info = engine.get_skill_info(skill_id)

    if not info:
        raise HTTPException(status_code=404, detail=f"Skill '{skill_id}' not found")

    return info.to_dict()


@router.post("/{skill_id}/execute")
async def execute_skill(skill_id: str, params: Dict[str, Any]):
    """执行技能"""
    engine = get_engine()
    result = await engine.execute(skill_id, params)

    if not result.success:
        raise HTTPException(status_code=400, detail=result.output)

    return {
        "success": result.success,
        "output": result.output,
        "skill_id": result.skill_id,
        "level_used": result.level_used,
    }


@router.get("/{skill_id}/versions")
async def get_skill_versions(skill_id: str):
    """获取技能的所有版本"""
    engine = get_engine()
    versions = engine.get_versions(skill_id)

    return {
        "skill_id": skill_id,
        "versions": [v.to_dict() for v in versions],
        "count": len(versions),
    }


@router.get("/{skill_id}/evolution")
async def get_evolution_history(skill_id: str):
    """获取技能进化历史"""
    engine = get_engine()
    records = engine.get_evolution_history(skill_id)

    return {
        "skill_id": skill_id,
        "records": [r.to_dict() for r in records],
        "count": len(records),
    }
