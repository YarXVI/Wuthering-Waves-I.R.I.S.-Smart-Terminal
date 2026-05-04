"""

MEMORY.md 记忆架构 - 环境事实和经验教训的持久化

参考 Hermes 的 MEMORY.md 模式

"""



import json

import re

from dataclasses import dataclass, field

from datetime import datetime

from pathlib import Path

from typing import Any



from agent_core.utils.filelock import locked_write





MEMORY_DIR = Path(__file__).resolve().parent.parent.parent / "memory"

MEMORY_FILE = MEMORY_DIR / "MEMORY.md"

USER_PREFERENCES_FILE = MEMORY_DIR / "USER.md"



DEFAULT_MEMORY_TEMPLATE = """# I.R.I.S. 记忆文档



> 本文件记录环境事实、经验教训和重要上下文



## 系统身份

- 名称: I.R.I.S. Smart Terminal

- 版本: 0.0.1-beta

- 角色: 智能工作助手



## 环境信息

{env_info}



## 重要事实

{facts}



## 经验教训

{lessons}



## 当前项目状态

{project_status}



---

最后更新: {updated_at}

"""



DEFAULT_USER_TEMPLATE = """# 用户偏好



> 本文件记录用户偏好和设置



## 用户信息

{user_info}



## 偏好设置

{preferences}



## 已知习惯

{habits}



---

最后更新: {updated_at}

"""





@dataclass

class MemoryEntry:

    """记忆条目"""

    category: str

    content: str

    priority: int = 5

    tags: list[str] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)





class MemoryScanner:

    """记忆安全扫描器 - 自动评估记忆安全性"""



    def __init__(self):

        self._sensitive_patterns = [

            (r"api[_-]?key", "API密钥"),

            (r"secret", "密钥"),

            (r"password", "密码"),

            (r"token", "访问令牌"),

            (r"credential", "凭证"),

        ]



    def scan(self, text: str) -> tuple[bool, list[str]]:

        """

        扫描文本中的敏感信息

        Returns: (is_safe, warnings)

        """

        warnings = []

        text_lower = text.lower()



        for pattern, name in self._sensitive_patterns:

            if re.search(pattern, text_lower):

                warnings.append(f"可能包含{name}信息")



        return len(warnings) == 0, warnings



    def sanitize(self, text: str) -> str:

        """清理敏感信息"""

        sanitized = text

        sensitive_patterns = [

            (r"(api[_-]?key['\"]?\s*[:=]\s*)['\"]?[\w-]{20,}['\"]?", r"\1[REDACTED]"),

            (r"(secret['\"]?\s*[:=]\s*)['\"]?[\w-]{20,}['\"]?", r"\1[REDACTED]"),

            (r"(password['\"]?\s*[:=]\s*)['\"]?[^\s'\"]{8,}['\"]?", r"\1[REDACTED]"),

            (r"(token['\"]?\s*[:=]\s*)['\"]?[\w-]{20,}['\"]?", r"\1[REDACTED]"),

        ]



        for pattern, replacement in sensitive_patterns:

            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)



        return sanitized





class MemoryManager:

    """MEMORY.md 记忆管理器"""



    def __init__(

        self,

        memory_file: Path | None = None,

        max_chars: int = 2200,

    ):

        self.memory_file = memory_file or MEMORY_FILE

        self.max_chars = max_chars

        self.scanner = MemoryScanner()

        self._ensure_file()



    def _ensure_file(self):

        """确保记忆文件存在"""

        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.memory_file.exists():

            self.memory_file.write_text(DEFAULT_MEMORY_TEMPLATE.format(

                env_info="- 尚未记录环境信息",

                facts="- 尚未记录重要事实",

                lessons="- 尚未记录经验教训",

                project_status="- 尚未记录项目状态",

                updated_at=datetime.now().isoformat(),

            ), encoding="utf-8")



    def load(self) -> dict[str, str]:

        """加载记忆内容"""

        if not self.memory_file.exists():

            return {}



        content = self.memory_file.read_text(encoding="utf-8")

        return self._parse_memory_content(content)



    def _parse_memory_content(self, content: str) -> dict[str, str]:

        """解析记忆文件内容"""

        sections = {}

        current_section = "header"

        current_content = []



        for line in content.split("\n"):

            if line.startswith("## "):

                if current_content or current_section != "header":

                    sections[current_section] = "\n".join(current_content).strip()

                current_section = line[3:].strip().lower()

                current_content = []

            else:

                current_content.append(line)



        if current_content:

            sections[current_section] = "\n".join(current_content).strip()



        return sections



    def save(self, sections: dict[str, str]) -> bool:

        """保存记忆内容"""

        try:

            lines = ["# I.R.I.S. 记忆文档", "", "> 本文件记录环境事实、经验教训和重要上下文", ""]



            section_order = ["系统身份", "环境信息", "重要事实", "经验教训", "当前项目状态"]



            for section in section_order:

                content = sections.get(section, f"- 尚未记录{section}")

                lines.append(f"## {section}")

                for line in content.split("\n"):

                    lines.append(line)

                lines.append("")



            lines.append(f"最后更新: {datetime.now().isoformat()}")



            content = "\n".join(lines)

            if len(content) > self.max_chars * 1.5:

                content = content[:self.max_chars * 2] + "\n\n[警告：记忆内容过长，已截断]"



            if not locked_write(self.memory_file, content):

                self.memory_file.write_text(content, encoding="utf-8")



            return True

        except Exception as e:

            print(f"[Memory] Failed to save memory: {e}")

            return False



    def add_fact(self, fact: str, priority: int = 5) -> bool:

        """添加重要事实"""

        is_safe, warnings = self.scanner.scan(fact)

        if not is_safe:

            print(f"[Memory] Warning: {warnings}")



        sections = self.load()

        facts_section = sections.get("重要事实", "")



        fact_entry = f"- [{priority}] {fact}"

        if fact_entry not in facts_section:

            facts_section += f"\n{fact_entry}"



        sections["重要事实"] = facts_section.strip()

        return self.save(sections)



    def add_lesson(self, lesson: str, priority: int = 5) -> bool:

        """添加经验教训"""

        sections = self.load()

        lessons_section = sections.get("经验教训", "")



        lesson_entry = f"- [{priority}] {lesson}"

        if lesson_entry not in lessons_section:

            lessons_section += f"\n{lesson_entry}"



        sections["经验教训"] = lessons_section.strip()

        return self.save(sections)



    def add_env_info(self, env_info: str) -> bool:

        """添加环境信息"""

        sections = self.load()

        sections["环境信息"] = env_info.strip()

        return self.save(sections)



    def set_project_status(self, status: str) -> bool:

        """设置项目状态"""

        sections = self.load()

        sections["当前项目状态"] = status.strip()

        return self.save(sections)



    def get_injected_memory(self) -> str:

        """获取用于注入到 Prompt 的记忆内容"""

        sections = self.load()



        parts = []

        for key in ["系统身份", "环境信息", "重要事实", "经验教训"]:

            if sections.get(key):

                parts.append(f"## {key}\n{sections[key]}")



        return "\n\n".join(parts) if parts else ""





class UserPreferencesManager:

    """USER.md 用户偏好管理器"""



    def __init__(self, preferences_file: Path | None = None):

        self.preferences_file = preferences_file or USER_PREFERENCES_FILE

        self.scanner = MemoryScanner()

        self._ensure_file()



    def _ensure_file(self):

        """确保用户偏好文件存在"""

        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)

        if not self.preferences_file.exists():

            self.preferences_file.write_text(DEFAULT_USER_TEMPLATE.format(

                user_info="- 尚未记录用户信息",

                preferences="- 尚未记录偏好设置",

                habits="- 尚未记录已知习惯",

                updated_at=datetime.now().isoformat(),

            ), encoding="utf-8")



    def load(self) -> dict[str, str]:

        """加载用户偏好"""

        if not self.preferences_file.exists():

            return {}



        content = self.preferences_file.read_text(encoding="utf-8")

        return self._parse_preferences_content(content)



    def _parse_preferences_content(self, content: str) -> dict[str, str]:

        """解析用户偏好文件内容"""

        sections = {}

        current_section = "header"

        current_content = []



        for line in content.split("\n"):

            if line.startswith("## "):

                if current_content or current_section != "header":

                    sections[current_section] = "\n".join(current_content).strip()

                current_section = line[3:].strip().lower()

                current_content = []

            else:

                current_content.append(line)



        if current_content:

            sections[current_section] = "\n".join(current_content).strip()



        return sections



    def save(self, sections: dict[str, str]) -> bool:

        """保存用户偏好"""

        try:

            lines = ["# 用户偏好", "", "> 本文件记录用户偏好和设置", ""]



            section_order = ["用户信息", "偏好设置", "已知习惯"]



            for section in section_order:

                content = sections.get(section, f"- 尚未记录{section}")

                lines.append(f"## {section}")

                for line in content.split("\n"):

                    lines.append(line)

                lines.append("")



            lines.append(f"最后更新: {datetime.now().isoformat()}")



            content = "\n".join(lines)



            if not locked_write(self.preferences_file, content):

                self.preferences_file.write_text(content, encoding="utf-8")



            return True

        except Exception as e:

            print(f"[UserPreferences] Failed to save preferences: {e}")

            return False



    def set_user_info(self, user_info: str) -> bool:

        """设置用户信息"""

        sections = self.load()

        sections["用户信息"] = user_info.strip()

        return self.save(sections)



    def add_preference(self, preference: str) -> bool:

        """添加偏好设置"""

        sections = self.load()

        prefs_section = sections.get("偏好设置", "")



        if preference not in prefs_section:

            prefs_section += f"\n- {preference}"



        sections["偏好设置"] = prefs_section.strip()

        return self.save(sections)



    def add_habit(self, habit: str) -> bool:

        """添加已知习惯"""

        sections = self.load()

        habits_section = sections.get("已知习惯", "")



        if habit not in habits_section:

            habits_section += f"\n- {habit}"



        sections["已知习惯"] = habits_section.strip()

        return self.save(sections)



    def learn_from_interaction(self, user_input: str, agent_response: str) -> bool:

        """从交互中学习用户偏好"""

        learned = False

        sections = self.load()



        if any(word in user_input.lower() for word in ["喜欢", " prefer", "，希望 ", " want "]):

            learned = True



        if any(word in agent_response.lower() for word in ["简洁", " brief", "详细", " detail"]):

            preference = "- 用户偏好简洁回复" if "简洁" in agent_response else "- 用户偏好详细回复"

            prefs = sections.get("偏好设置", "")

            if preference not in prefs:

                prefs += f"\n{preference}"

                sections["偏好设置"] = prefs.strip()

                learned = True



        if learned:

            return self.save(sections)



        return False



    def get_injected_preferences(self) -> str:

        """获取用于注入到 Prompt 的用户偏好"""

        sections = self.load()



        parts = []

        for key in ["用户信息", "偏好设置", "已知习惯"]:

            if sections.get(key):

                parts.append(f"## {key}\n{sections[key]}")



        return "\n\n".join(parts) if parts else ""





_memory_manager: MemoryManager | None = None

_user_preferences_manager: UserPreferencesManager | None = None





def get_memory_manager() -> MemoryManager:

    """获取全局记忆管理器单例"""

    global _memory_manager

    if _memory_manager is None:

        _memory_manager = MemoryManager()

    return _memory_manager





def get_user_preferences_manager() -> UserPreferencesManager:

    """获取全局用户偏好管理器单例"""

    global _user_preferences_manager

    if _user_preferences_manager is None:

        _user_preferences_manager = UserPreferencesManager()

    return _user_preferences_manager

