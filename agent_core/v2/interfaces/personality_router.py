"""
Router: Personality API

Personality management endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from agent_core.v2.domain.personality import (
    PersonalityRegistry, Personality, PersonalityTrait, ValueStatement,
    BehaviorConfig, BoundaryRule, CommunicationStyle, HumorLevel, ResponseLength
)

router = APIRouter(prefix="/personality", tags=["personality"])


class PersonalityCreateRequest(BaseModel):
    """创建人格请求"""
    id: str
    name: str
    role: str
    description: str = ""
    traits: List[Dict[str, Any]] = []
    values: List[Dict[str, Any]] = []
    behaviors: Dict[str, Any] = {}
    boundaries: List[Dict[str, Any]] = []


class LLMParamsRequest(BaseModel):
    """LLM 参数请求"""
    agent_id: str
    params: Dict[str, Any]


def get_registry():
    """获取人格注册表"""
    return PersonalityRegistry()


@router.get("/list")
async def list_personalities():
    """列出所有可用的人格"""
    registry = get_registry()
    personalities = registry.list_all()

    return {
        "personalities": [
            {
                "id": p.id,
                "name": p.name,
                "role": p.role,
                "description": p.description,
                "traits_count": len(p.traits),
                "values_count": len(p.values),
                "is_builtin": p.id in ("iris", "professional", "creative"),
            }
            for p in personalities
        ],
        "total": len(personalities),
        "builtin_ids": ["iris", "professional", "creative"],
    }


@router.get("/{personality_id}")
async def get_personality(personality_id: str):
    """获取指定人格详情"""
    registry = get_registry()
    personality = registry.get(personality_id)

    if not personality:
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")

    return _personality_to_dict(personality)


@router.post("/create")
async def create_personality(req: PersonalityCreateRequest):
    """创建新的人格"""
    registry = get_registry()

    behaviors_data = req.behaviors or {}
    behaviors = BehaviorConfig(
        communication_style=CommunicationStyle(behaviors_data.get("communication_style", "friendly")),
        humor_level=HumorLevel(behaviors_data.get("humor_level", "subtle")),
        response_length=ResponseLength(behaviors_data.get("response_length", "medium")),
        formality=behaviors_data.get("formality", 0.5),
        temperature_modifier=behaviors_data.get("temperature_modifier", 0.0),
        max_tokens_modifier=behaviors_data.get("max_tokens_modifier", 0),
    )

    personality = Personality(
        id=req.id,
        name=req.name,
        role=req.role,
        description=req.description,
        traits=[PersonalityTrait(**t) for t in req.traits],
        values=[ValueStatement(**v) for v in req.values],
        behaviors=behaviors,
        boundaries=[BoundaryRule(**b) for b in req.boundaries],
    )

    registry.register(personality)
    return {"success": True, "personality": _personality_to_dict(personality)}


@router.delete("/{personality_id}")
async def delete_personality(personality_id: str):
    """删除人格（内置人格不可删除）"""
    registry = get_registry()
    success = registry.unregister(personality_id)

    if not success:
        if personality_id in ("iris", "professional", "creative"):
            raise HTTPException(status_code=403, detail="Cannot delete built-in personalities")
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")

    return {"success": True, "deleted": personality_id}


@router.get("/{personality_id}/prompt")
async def get_personality_prompt(personality_id: str):
    """获取人格的系统提示词"""
    registry = get_registry()
    personality = registry.get(personality_id)

    if not personality:
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")

    return {
        "personality_id": personality_id,
        "prompt": personality.generate_system_prompt(),
        "llm_params": personality.get_llm_params(),
    }


@router.get("/{personality_id}/llm-params")
async def get_llm_params(personality_id: str):
    """获取人格的 LLM 参数调整"""
    registry = get_registry()
    personality = registry.get(personality_id)

    if not personality:
        raise HTTPException(status_code=404, detail=f"Personality '{personality_id}' not found")

    return {
        "personality_id": personality_id,
        "llm_params": personality.get_llm_params(),
    }


def _personality_to_dict(personality: Personality) -> Dict[str, Any]:
    """将 Personality 对象转换为字典"""
    return {
        "id": personality.id,
        "name": personality.name,
        "role": personality.role,
        "description": personality.description,
        "traits": [t.to_dict() for t in personality.traits] if personality.traits else [],
        "values": [v.to_dict() for v in personality.values] if personality.values else [],
        "behaviors": personality.behaviors.to_dict() if personality.behaviors else {},
        "boundaries": [b.to_dict() for b in personality.boundaries] if personality.boundaries else [],
    }
