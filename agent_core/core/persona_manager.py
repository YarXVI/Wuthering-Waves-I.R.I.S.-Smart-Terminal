"""

Persona 管理器 - Agent 人格切换管理

支持动态切换不同的人格配置

"""



import threading

from pathlib import Path

from typing import Callable



from agent_core.core.personality import (

    AgentProfileData,

    PersonalityConfig,

    create_default_personality,

    create_professional_personality,

    create_friendly_personality,

)

from agent_core.core.profile_loader import ProfileLoader, get_profile_loader





class PersonaManager:

    """人格切换管理器"""



    def __init__(self):

        self._personas: dict[str, AgentProfileData] = {}

        self._current_id: str | None = None

        self._lock = threading.RLock()

        self._profile_loader = get_profile_loader()

        self._listeners: list[Callable[[str, AgentProfileData], None]] = []



        self._register_builtin_personas()



    def _register_builtin_personas(self):

        """注册内置人格"""

        default_profile = AgentProfileData(

            id="default",

            name="I.R.I.S.",

            role="智能工作助手",

            personality=create_default_personality(),

            metadata={"builtin": True},

        )

        self._personas["default"] = default_profile



        professional_profile = AgentProfileData(

            id="professional",

            name="I.R.I.S. 专业版",

            role="专业顾问",

            personality=create_professional_personality(),

            metadata={"builtin": True},

        )

        self._personas["professional"] = professional_profile



        friendly_profile = AgentProfileData(

            id="friendly",

            name="I.R.I.S. 友好版",

            role="友好助手",

            personality=create_friendly_personality(),

            metadata={"builtin": True},

        )

        self._personas["friendly"] = friendly_profile



    def register_persona(self, profile: AgentProfileData) -> bool:

        """注册新人格"""

        with self._lock:

            if profile.id in self._personas and not profile.metadata.get("builtin"):

                existing = self._personas[profile.id]

                if existing.metadata.get("locked"):

                    return False



            self._personas[profile.id] = profile

            return True



    def unregister_persona(self, persona_id: str) -> bool:

        """注销人格"""

        with self._lock:

            if persona_id not in self._personas:

                return False



            profile = self._personas[persona_id]

            if profile.metadata.get("locked"):

                return False



            if self._current_id == persona_id:

                self._current_id = "default"



            del self._personas[persona_id]

            return True



    def switch_persona(self, persona_id: str) -> bool:

        """切换人格"""

        with self._lock:

            if persona_id not in self._personas:

                return False



            old_id = self._current_id

            old_profile = self._personas.get(old_id)

            self._current_id = persona_id



            self._notify_listeners(old_id, old_profile)



            return True



    def get_current_persona(self) -> AgentProfileData | None:

        """获取当前人格"""

        with self._lock:

            if self._current_id is None:

                return self._personas.get("default")

            return self._personas.get(self._current_id)



    def get_persona(self, persona_id: str) -> AgentProfileData | None:

        """获取指定人格"""

        with self._lock:

            return self._personas.get(persona_id)



    def list_personas(self) -> list[dict]:

        """列出所有已注册人格"""

        with self._lock:

            return [

                {

                    "id": p.id,

                    "name": p.name,

                    "role": p.role,

                    "is_current": p.id == self._current_id,

                    "is_builtin": p.metadata.get("builtin", False),

                }

                for p in self._personas.values()

            ]



    def load_persona_from_file(self, path: Path) -> AgentProfileData | None:

        """从文件加载人格"""

        profile = self._profile_loader.load(path)

        if profile:

            self.register_persona(profile)

        return profile



    def export_persona(self, persona_id: str, path: Path) -> bool:

        """导出自定义人格到文件"""

        with self._lock:

            profile = self._personas.get(persona_id)

            if not profile:

                return False



            if profile.metadata.get("builtin"):

                return False



            try:

                content = self._persona_to_markdown(profile)

                path.parent.mkdir(parents=True, exist_ok=True)

                path.write_text(content, encoding="utf-8")

                return True

            except Exception as e:

                print(f"[PersonaManager] Failed to export persona: {e}")

                return False



    def _persona_to_markdown(self, profile: AgentProfileData) -> str:

        """将人格转换为 Markdown 格式"""

        lines = [

            "---",

            f"id: {profile.id}",

            f"name: {profile.name}",

            f"role: {profile.role}",

            f'version: "{profile.metadata.get("version", "1.0")}"',

            "---",

            "",

            f"# {profile.name}",

            "",

            f"**角色**: {profile.role}",

            "",

            "## 性格特征",

        ]



        for trait in profile.personality.traits:

            lines.append(f"- {trait.name}: {trait.description}")



        lines.extend([

            "",

            f"## 沟通风格",

            f"- {profile.personality.communication_style.value}",

            "",

            f"## 幽默程度",

            f"- {profile.personality.humor_level.value}",

        ])



        if profile.values:

            lines.append("")

            lines.append("## 价值观")

            for v in profile.values:

                lines.append(f"- {v.principle}")



        if profile.boundaries:

            lines.append("")

            lines.append("## 行为边界")

            for b in profile.boundaries:

                lines.append(f"- {b.rule}")



        system_prompt = profile.metadata.get("system_prompt", "")

        if system_prompt:

            lines.extend([

                "",

                "## 系统提示词",

                "",

                system_prompt,

            ])



        return "\n".join(lines)



    def add_listener(self, listener: Callable[[str, AgentProfileData], None]):

        """添加人格切换监听器"""

        if listener not in self._listeners:

            self._listeners.append(listener)



    def remove_listener(self, listener: Callable[[str, AgentProfileData], None]):

        """移除人格切换监听器"""

        if listener in self._listeners:

            self._listeners.remove(listener)



    def _notify_listeners(self, old_id: str | None, old_profile: AgentProfileData | None):

        """通知监听器人格切换"""

        for listener in self._listeners:

            try:

                listener(old_id or "", old_profile)

            except Exception as e:

                print(f"[PersonaManager] Listener error: {e}")



    def lock_persona(self, persona_id: str) -> bool:

        """锁定人格（防止被删除）"""

        with self._lock:

            if persona_id not in self._personas:

                return False

            self._personas[persona_id].metadata["locked"] = True

            return True



    def unlock_persona(self, persona_id: str) -> bool:

        """解锁人格"""

        with self._lock:

            if persona_id not in self._personas:

                return False

            if self._personas[persona_id].metadata.get("builtin"):

                return False

            self._personas[persona_id].metadata["locked"] = False

            return True





_persona_manager: PersonaManager | None = None





def get_persona_manager() -> PersonaManager:

    """获取全局人格管理器单例"""

    global _persona_manager

    if _persona_manager is None:

        _persona_manager = PersonaManager()

    return _persona_manager





def switch_persona(persona_id: str) -> bool:

    """便捷函数：切换人格"""

    return get_persona_manager().switch_persona(persona_id)





def get_current_persona() -> AgentProfileData | None:

    """便捷函数：获取当前人格"""

    return get_persona_manager().get_current_persona()

