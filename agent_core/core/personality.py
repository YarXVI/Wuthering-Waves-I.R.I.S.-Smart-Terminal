"""

人格配置数据结构 - 定义 Agent 人格相关的数据结构

"""



from dataclasses import dataclass, field

from enum import Enum

from typing import Any





class CommunicationStyle(str, Enum):

    """沟通风格"""

    FORMAL = "formal"           # 正式

    CASUAL = "casual"          # 随意

    FRIENDLY = "friendly"      # 友好

    PROFESSIONAL = "professional"  # 专业

    CONCISE = "concise"         # 简洁

    DETAILED = "detailed"       # 详细





class HumorLevel(str, Enum):

    """幽默程度"""

    NONE = "none"               # 无

    LOW = "low"                 # 偏低

    MODERATE = "moderate"       # 适中

    HIGH = "high"               # 偏高





class ResponseLength(str, Enum):

    """回复长度偏好"""

    SHORT = "short"             # 简短

    MEDIUM = "medium"           # 中等

    LONG = "long"               # 详细





@dataclass

class PersonalityTrait:

    """人格特征"""

    name: str                    # 特征名称

    description: str = ""        # 特征描述

    intensity: float = 0.5      # 强度 0.0-1.0





@dataclass

class BehaviorConfig:

    """行为配置"""

    max_iterations: int = 10           # 最大迭代次数

    default_temperature: float = 0.3   # 默认温度

    response_length: ResponseLength = ResponseLength.MEDIUM

    enable_small_talk: bool = True     # 是否允许闲聊

    proactive_hints: bool = True       # 是否主动给出提示

    confirmation_threshold: float = 0.7  # 确认阈值





@dataclass

class PersonalityConfig:

    """人格配置"""

    traits: list[PersonalityTrait] = field(default_factory=list)

    communication_style: CommunicationStyle = CommunicationStyle.FRIENDLY

    humor_level: HumorLevel = HumorLevel.MODERATE

    response_length: ResponseLength = ResponseLength.MEDIUM

    default_greeting: str = "你好！有什么我可以帮你的吗？"

    default_farewell: str = "再见！祝你有美好的一天！"

    preferred_pronouns: tuple[str, str] = ("你", "我")  # (对方, 自己)



    def get_trait_names(self) -> list[str]:

        """获取所有特征名称"""

        return [t.name for t in self.traits]



    def get_trait_description(self, trait_name: str) -> str | None:

        """获取特定特征的描述"""

        for trait in self.traits:

            if trait.name == trait_name:

                return trait.description

        return None



    def to_prompt_segments(self) -> list[str]:

        """转换为 Prompt 片段"""

        segments = []



        if self.traits:

            trait_strs = [f"- {t.name}: {t.description}" for t in self.traits]

            segments.append("## 性格特征\n" + "\n".join(trait_strs))



        segments.append(f"## 沟通风格\n- {self.communication_style.value}")



        if self.humor_level != HumorLevel.NONE:

            segments.append(f"## 幽默程度\n- {self.humor_level.value}")



        segments.append(f"## 回复长度\n- {self.response_length.value}")



        if self.default_greeting:

            segments.append(f"## 问候语\n{self.default_greeting}")



        return segments





@dataclass

class ValueStatement:

    """价值观陈述"""

    principle: str              # 原则

    description: str = ""       # 描述

    priority: int = 5           # 优先级





@dataclass

class BoundaryRule:

    """边界规则"""

    rule: str                    # 规则内容

    reason: str = ""             # 原因

    strictness: float = 1.0     # 严格程度 0.0-1.0





@dataclass

class AgentProfileData:

    """Agent档案数据结构 - 运行时使用"""

    id: str

    name: str

    role: str

    personality: PersonalityConfig

    values: list[ValueStatement] = field(default_factory=list)

    behaviors: BehaviorConfig = field(default_factory=BehaviorConfig)

    boundaries: list[BoundaryRule] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)



    def get_value_principles(self) -> list[str]:

        """获取价值观原则列表"""

        sorted_values = sorted(self.values, key=lambda v: v.priority, reverse=True)

        return [v.principle for v in sorted_values]



    def get_boundary_rules(self) -> list[str]:

        """获取边界规则列表"""

        return [b.rule for b in self.boundaries]



    def to_system_prompt(self) -> str:

        """生成系统提示词"""

        parts = [f"# {self.name} - {self.role}"]



        parts.append("\n## 身份")

        parts.append(f"你是一个名为「{self.name}」的{self.role}。")



        parts.append("\n" + "\n".join(self.personality.to_prompt_segments()))



        if self.values:

            parts.append("\n## 价值观")

            for v in self.values:

                parts.append(f"- {v.principle}: {v.description}")



        if self.boundaries:

            parts.append("\n## 行为边界")

            for b in self.boundaries:

                parts.append(f"- {b.rule}")



        if self.metadata.get("system_prompt"):

            parts.append("\n" + self.metadata["system_prompt"])



        return "\n".join(parts)





def create_default_personality() -> PersonalityConfig:

    """创建默认人格配置"""

    return PersonalityConfig(

        traits=[

            PersonalityTrait(

                name="专业",

                description="提供准确、专业的信息和建议",

                intensity=0.8,

            ),

            PersonalityTrait(

                name="友善",

                description="友好、耐心地与用户交流",

                intensity=0.7,

            ),

            PersonalityTrait(

                name="高效",

                description="快速响应，减少不必要的来回",

                intensity=0.6,

            ),

        ],

        communication_style=CommunicationStyle.FRIENDLY,

        humor_level=HumorLevel.MODERATE,

        response_length=ResponseLength.MEDIUM,

    )





def create_professional_personality() -> PersonalityConfig:

    """创建专业人格配置"""

    return PersonalityConfig(

        traits=[

            PersonalityTrait(

                name="严谨",

                description="提供准确、经过验证的信息",

                intensity=0.9,

            ),

            PersonalityTrait(

                name="专业",

                description="使用专业术语，确保表达准确",

                intensity=0.8,

            ),

        ],

        communication_style=CommunicationStyle.PROFESSIONAL,

        humor_level=HumorLevel.NONE,

        response_length=ResponseLength.DETAILED,

    )





def create_friendly_personality() -> PersonalityConfig:

    """创建友好人格配置"""

    return PersonalityConfig(

        traits=[

            PersonalityTrait(

                name="热情",

                description="积极主动，帮助用户解决问题",

                intensity=0.8,

            ),

            PersonalityTrait(

                name="亲切",

                description="友好、耐心地与用户交流",

                intensity=0.9,

            ),

        ],

        communication_style=CommunicationStyle.FRIENDLY,

        humor_level=HumorLevel.MODERATE,

        response_length=ResponseLength.MEDIUM,

        default_greeting="你好！很高兴见到你！有什么我可以帮你的吗？",

    )

