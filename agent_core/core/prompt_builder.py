"""

Prompt 构建器 - 动态构建和优化系统提示词

支持技能注入、关键信息标记、个性化定制

"""



from dataclasses import dataclass, field

from typing import Any





@dataclass

class PromptConfig:

    """Prompt 配置"""

    include_skills: bool = True

    include_critical_info: bool = True

    max_length: int = 4000

    skill_injection_mode: str = "auto"

    personality_hints: str = ""





class PromptBuilder:

    """Prompt 构建器"""



    def __init__(self, base_prompt: str = ""):

        self._base_prompt = base_prompt

        self._skills: list[str] = []

        self._critical_info: list[str] = []

        self._personality: list[str] = []

        self._context: dict[str, Any] = {}



    def set_base(self, prompt: str) -> "PromptBuilder":

        """设置基础 Prompt"""

        self._base_prompt = prompt

        return self



    def add_skill(self, skill: str) -> "PromptBuilder":

        """添加技能描述"""

        if skill not in self._skills:

            self._skills.append(skill)

        return self



    def add_skills(self, skills: list[str]) -> "PromptBuilder":

        """批量添加技能"""

        for skill in skills:

            self.add_skill(skill)

        return self



    def add_critical_info(self, info: str) -> "PromptBuilder":

        """添加关键信息"""

        if info not in self._critical_info:

            self._critical_info.append(info)

        return self



    def add_personality(self, trait: str) -> "PromptBuilder":

        """添加人格特征"""

        if trait not in self._personality:

            self._personality.append(trait)

        return self



    def set_context(self, key: str, value: Any) -> "PromptBuilder":

        """设置上下文变量"""

        self._context[key] = value

        return self



    def build(self) -> str:

        """构建最终 Prompt"""

        parts = []



        if self._base_prompt:

            parts.append(self._base_prompt)



        if self._personality:

            parts.append("## 性格特征")

            parts.append(", ".join(self._personality))



        if self._skills:

            parts.append("## 可用技能")

            for skill in self._skills:

                parts.append(f"- {skill}")



        if self._critical_info:

            parts.append("## 关键信息")

            for info in self._critical_info:

                parts.append(f"- {info}")



        if self._context:

            parts.append("## 当前上下文")

            for key, value in self._context.items():

                parts.append(f"- {key}: {value}")



        result = "\n\n".join(parts)



        max_len = self._context.get("max_length", 4000)

        if len(result) > max_len * 2:

            result = result[:max_len * 2] + "\n\n[提示：上下文过长，已截断]"



        return result





class SkillInjector:

    """技能注入器"""



    def __init__(self, skill_registry=None):

        self._registry = skill_registry

        self._skill_cache: dict[str, str] = {}



    def inject(

        self,

        system_prompt: str,

        user_input: str,

        current_context: str,

    ) -> str:

        """注入匹配的技能说明"""

        if not self._registry:

            return system_prompt



        try:

            matched_skills = self._registry.get_matched_skills(user_input)

        except Exception:

            matched_skills = []



        if not matched_skills:

            return system_prompt



        skill_section = "\n\n## 匹配的技能说明\n"

        for skill in matched_skills:

            skill_section += f"\n### {skill.get('name', 'Unknown')}\n"

            skill_section += f"{skill.get('description', '')}\n"



        if len(system_prompt) + len(skill_section) < 4000:

            return system_prompt + skill_section



        return system_prompt





class DynamicPromptOptimizer:

    """动态 Prompt 优化器"""



    def __init__(self, llm_client=None):

        self._llm_client = llm_client



    def optimize(

        self,

        prompt: str,

        user_input: str,

        max_length: int = 4000,

    ) -> str:

        """优化 Prompt 长度和效果"""

        if len(prompt) <= max_length:

            return prompt



        if not self._llm_client:

            return self._naive_truncate(prompt, max_length)



        return self._llm_assisted_compress(prompt, user_input, max_length)



    def _naive_truncate(self, prompt: str, max_length: int) -> str:

        """简单截断"""

        return prompt[:max_length] + "\n\n[内容已截断]"



    def _llm_assisted_compress(

        self,

        prompt: str,

        user_input: str,

        max_length: int,

    ) -> str:

        """LLM 辅助压缩"""

        compress_prompt = f"""请精简以下系统提示词，保留关键信息，压缩到 {max_length} 字符以内：



当前提示词：

{prompt}



用户输入：

{user_input}



请输出精简后的版本："""



        try:

            response = self._llm_client.chat(

                [{"role": "user", "content": compress_prompt}],

                temperature=0.3,

            )

            if isinstance(response, dict):

                return response.get("content", prompt)[:max_length]

            return str(response)[:max_length]

        except Exception:

            return self._naive_truncate(prompt, max_length)





def create_agent_prompt(

    agent_name: str = "助手",

    agent_role: str = "智能工作助手",

    skills: list[str] | None = None,

    rules: list[str] | None = None,

) -> str:

    """创建标准 Agent Prompt"""

    parts = [

        f"你是一个名为「{agent_name}」的{agent_role}。",

        "",

        "## 工作原则",

        "- 接到任务后，先理解用户真正想要什么",

        "- 如果信息不够，主动追问",

        "- 如果需要查阅资料，使用工具搜索和读取",

        "- 整理信息后，给出清晰、结构化的回答",

        "- 找不到就说找不到，不编造信息",

        "",

        "## 输出要求",

        "- 结构化：使用标题、列表、代码块等组织内容",

        "- 有价值：给出见解和建议，不只是罗列信息",

        "- 诚实：不知道就说不知道",

    ]



    if skills:

        parts.append("")

        parts.append("## 可用工具")

        for skill in skills:

            parts.append(f"- {skill}")



    if rules:

        parts.append("")

        parts.append("## 额外规则")

        for rule in rules:

            parts.append(f"- {rule}")



    return "\n".join(parts)

