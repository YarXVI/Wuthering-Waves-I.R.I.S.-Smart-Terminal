"""
Skills Registry �?技能注册表
�?skills/ 目录发现并注册可用技能�?
"""

import os
from pathlib import Path
from typing import Callable, Optional

# skills/ 目录在项目根目录（agent-core 同级或上级）
SKILLS_DIR = Path(__file__).parent.parent.parent.parent.parent / "skills"
# 如果上面路径不存在，尝试 WORKSPACE/skills
if not SKILLS_DIR.exists():
    SKILLS_DIR = Path(__file__).parent.parent.parent.parent / "skills"
# 最后的兜底
if not SKILLS_DIR.exists():
    SKILLS_DIR = Path.home() / "agent办公�? / "skills"


class SkillInfo:
    """技能信�?""

    def __init__(self, name: str, path: Path):
        self.name = name
        self.path = path
        self.description = ""
        self.enabled = True
        self._load_meta()

    def _load_meta(self):
        """�?SKILL.md 加载元信�?""
        skill_md = self.path / "SKILL.md"
        if skill_md.exists():
            try:
                with open(skill_md, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        self.description = first_line[2:].strip()
                    else:
                        self.description = first_line[:100]
            except Exception:
                self.description = self.name


class SkillsRegistry:
    """技能注册表 �?扫描 skills/ 目录"""

    def __init__(self):
        self._skills: dict[str, SkillInfo] = {}
        self._scan()

    def _scan(self):
        """扫描 skills/ 目录"""
        if not SKILLS_DIR.exists():
            return

        for item in SKILLS_DIR.iterdir():
            if item.is_dir() and (item / "SKILL.md").exists():
                skill = SkillInfo(item.name, item)
                self._skills[skill.name] = skill

    def list_skills(self) -> list[dict]:
        """列出所有可用技�?""
        return [
            {
                "name": s.name,
                "description": s.description,
                "enabled": s.enabled,
                "path": str(s.path),
            }
            for s in self._skills.values()
        ]

    def get_skill(self, name: str) -> Optional[SkillInfo]:
        return self._skills.get(name)

    def enable_skill(self, name: str, enabled: bool) -> bool:
        """启用/禁用技�?""
        skill = self._skills.get(name)
        if not skill:
            return False
        skill.enabled = enabled
        return True

    def get_enabled_skills(self) -> list[SkillInfo]:
        return [s for s in self._skills.values() if s.enabled]

    def refresh(self):
        """重新扫描技能目�?""
        self._skills.clear()
        self._scan()


# 全局单例
skills_registry = SkillsRegistry()
