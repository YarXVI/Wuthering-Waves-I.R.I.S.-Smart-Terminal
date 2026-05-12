"""
Personality System

Agent personality configuration with traits, values, behaviors, and boundaries.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional
from pathlib import Path
import json


class CommunicationStyle(str, Enum):
    """沟通风格"""
    FORMAL = "formal"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    DRY = "dry"


class HumorLevel(str, Enum):
    """幽默程度"""
    NONE = "none"
    SUBTLE = "subtle"
    MODERATE = "moderate"
    HIGH = "high"


class ResponseLength(str, Enum):
    """响应长度偏好"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


@dataclass
class PersonalityTrait:
    """人格特质"""
    name: str
    description: str
    intensity: float = 0.5  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description, "intensity": self.intensity}


@dataclass
class ValueStatement:
    """价值声明"""
    value: str
    priority: int = 1  # 1-5

    def to_dict(self) -> Dict[str, Any]:
        return {"value": self.value, "priority": self.priority}


@dataclass
class BoundaryRule:
    """行为边界规则"""
    rule: str
    severity: str = "warning"  # warning, error, critical

    def to_dict(self) -> Dict[str, Any]:
        return {"rule": self.rule, "severity": self.severity}


@dataclass
class BehaviorConfig:
    """行为配置"""
    communication_style: CommunicationStyle = CommunicationStyle.FRIENDLY
    humor_level: HumorLevel = HumorLevel.SUBTLE
    response_length: ResponseLength = ResponseLength.MEDIUM
    formality: float = 0.5  # 0-1
    temperature_modifier: float = 0.0  # 对 LLM temperature 的微调
    max_tokens_modifier: int = 0  # 对 max_tokens 的微调

    def to_dict(self) -> Dict[str, Any]:
        return {
            "communication_style": self.communication_style.value,
            "humor_level": self.humor_level.value,
            "response_length": self.response_length.value,
            "formality": self.formality,
            "temperature_modifier": self.temperature_modifier,
            "max_tokens_modifier": self.max_tokens_modifier,
        }


@dataclass
class Personality:
    """
    人格配置 —— Agent 的核心属性

    直接生成系统提示词片段，注入到 AgentRuntime 的 system prompt 中
    """
    id: str
    name: str
    role: str
    traits: List[PersonalityTrait] = field(default_factory=list)
    values: List[ValueStatement] = field(default_factory=list)
    behaviors: BehaviorConfig = field(default_factory=BehaviorConfig)
    boundaries: List[BoundaryRule] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "traits": [t.to_dict() for t in self.traits],
            "values": [v.to_dict() for v in self.values],
            "behaviors": self.behaviors.to_dict(),
            "boundaries": [b.to_dict() for b in self.boundaries],
            "description": self.description,
        }

    def generate_system_prompt(self) -> str:
        """生成人格系统提示词片段"""
        parts = [f"你是 {self.name}，一个{self.role}。"]

        if self.description:
            parts.append(f"\n## 描述\n{self.description}")

        if self.traits:
            traits_str = "\n".join([f"- {t.name}: {t.description} (强度: {int(t.intensity * 100)}%)" for t in self.traits])
            parts.append(f"\n## 人格特质\n{traits_str}")

        if self.values:
            values_str = "\n".join([f"{v.priority}. {v.value}" for v in sorted(self.values, key=lambda x: -x.priority)])
            parts.append(f"\n## 核心价值观\n{values_str}")

        behaviors = self.behaviors
        parts.append(f"\n## 沟通风格\n"
                     f"- 风格: {behaviors.communication_style.value}\n"
                     f"- 幽默感: {behaviors.humor_level.value}\n"
                     f"- 响应长度: {behaviors.response_length.value}\n"
                     f"- 正式程度: {int(behaviors.formality * 100)}%")

        if self.boundaries:
            boundaries_str = "\n".join([f"- {b.rule} ({b.severity})" for b in self.boundaries])
            parts.append(f"\n## 行为边界\n{boundaries_str}")

        return "\n".join(parts)

    def get_llm_params(self) -> Dict[str, Any]:
        """根据人格获取 LLM 参数调整"""
        params = {}
        if self.behaviors.temperature_modifier != 0:
            params["temperature"] = 0.7 + self.behaviors.temperature_modifier
        if self.behaviors.max_tokens_modifier != 0:
            params["max_tokens"] = 4096 + self.behaviors.max_tokens_modifier
        return params


class PersonalityRegistry:
    """人格注册表 —— 管理所有可用人格"""

    def __init__(self, storage_dir: Optional[Path] = None):
        self.storage_dir = storage_dir or Path.home() / ".iris" / "personalities"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._personalities: Dict[str, Personality] = {}
        self._load_builtin_personalities()
        self._load_from_disk()

    def _load_builtin_personalities(self) -> None:
        """加载内置人格"""
        builtins = [
            Personality(
                id="iris",
                name="IRIS",
                role="智能助手",
                description="IRIS 系统默认人格，友好、专业、乐于助人",
                traits=[
                    PersonalityTrait("友好", "对用户友好热情", 0.8),
                    PersonalityTrait("专业", "在技术上保持专业", 0.9),
                    PersonalityTrait("耐心", "耐心解答问题", 0.7),
                ],
                values=[
                    ValueStatement("用户第一", 5),
                    ValueStatement("准确至上", 4),
                    ValueStatement("持续学习", 3),
                ],
                behaviors=BehaviorConfig(
                    communication_style=CommunicationStyle.FRIENDLY,
                    humor_level=HumorLevel.SUBTLE,
                    response_length=ResponseLength.MEDIUM,
                    formality=0.5,
                ),
            ),
            Personality(
                id="professional",
                name="Pro",
                role="专业顾问",
                description="正式、严谨的专业顾问人格",
                traits=[
                    PersonalityTrait("严谨", "逻辑严密，措辞准确", 0.9),
                    PersonalityTrait("高效", "直奔主题，不拖泥带水", 0.8),
                ],
                values=[
                    ValueStatement("准确至上", 5),
                    ValueStatement("效率优先", 4),
                ],
                behaviors=BehaviorConfig(
                    communication_style=CommunicationStyle.PROFESSIONAL,
                    humor_level=HumorLevel.NONE,
                    response_length=ResponseLength.SHORT,
                    formality=0.9,
                    temperature_modifier=-0.2,
                ),
            ),
            Personality(
                id="creative",
                name="Muse",
                role="创意伙伴",
                description="富有创造力、思维活跃的创意伙伴",
                traits=[
                    PersonalityTrait("创造力", "善于提出新颖想法", 0.9),
                    PersonalityTrait("热情", "对创意充满热情", 0.8),
                    PersonalityTrait("联想", "善于联想和类比", 0.7),
                ],
                values=[
                    ValueStatement("创新至上", 5),
                    ValueStatement("开放思维", 4),
                ],
                behaviors=BehaviorConfig(
                    communication_style=CommunicationStyle.ENTHUSIASTIC,
                    humor_level=HumorLevel.MODERATE,
                    response_length=ResponseLength.LONG,
                    formality=0.3,
                    temperature_modifier=0.2,
                ),
            ),
        ]
        for p in builtins:
            self._personalities[p.id] = p

    def _load_from_disk(self) -> None:
        """从磁盘加载自定义人格"""
        for f in self.storage_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                personality = self._dict_to_personality(data)
                self._personalities[personality.id] = personality
            except Exception:
                continue

    def _save_to_disk(self, personality: Personality) -> None:
        """保存人格到磁盘"""
        file_path = self.storage_dir / f"{personality.id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(personality.to_dict(), f, ensure_ascii=False, indent=2)

    def _dict_to_personality(self, data: Dict[str, Any]) -> Personality:
        """从字典创建人格"""
        behaviors_data = data.get("behaviors", {})
        behaviors = BehaviorConfig(
            communication_style=CommunicationStyle(behaviors_data.get("communication_style", "friendly")),
            humor_level=HumorLevel(behaviors_data.get("humor_level", "subtle")),
            response_length=ResponseLength(behaviors_data.get("response_length", "medium")),
            formality=behaviors_data.get("formality", 0.5),
            temperature_modifier=behaviors_data.get("temperature_modifier", 0.0),
            max_tokens_modifier=behaviors_data.get("max_tokens_modifier", 0),
        )

        return Personality(
            id=data["id"],
            name=data["name"],
            role=data["role"],
            description=data.get("description", ""),
            traits=[PersonalityTrait(**t) for t in data.get("traits", [])],
            values=[ValueStatement(**v) for v in data.get("values", [])],
            behaviors=behaviors,
            boundaries=[BoundaryRule(**b) for b in data.get("boundaries", [])],
        )

    def get(self, personality_id: str) -> Optional[Personality]:
        """获取人格"""
        return self._personalities.get(personality_id)

    def register(self, personality: Personality) -> None:
        """注册人格"""
        self._personalities[personality.id] = personality
        self._save_to_disk(personality)

    def unregister(self, personality_id: str) -> bool:
        """注销人格（内置人格不可删除）"""
        if personality_id in ("iris", "professional", "creative"):
            return False
        if personality_id in self._personalities:
            del self._personalities[personality_id]
            file_path = self.storage_dir / f"{personality_id}.json"
            if file_path.exists():
                file_path.unlink()
            return True
        return False

    def list_all(self) -> List[Personality]:
        """列出所有人格"""
        return list(self._personalities.values())

    def list_ids(self) -> List[str]:
        """列出所有人格 ID"""
        return list(self._personalities.keys())
