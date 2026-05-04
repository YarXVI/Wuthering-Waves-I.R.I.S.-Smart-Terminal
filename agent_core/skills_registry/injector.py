"""
Skills Injector - Injects skills into agents
"""

from typing import Dict, Any, Optional


class SkillInjector:
    """Injects skills into agent context"""

    def inject_skill(self, skill_def: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Inject a skill into agent context"""
        return True

    def extract_skills(self, prompt: str) -> list[str]:
        """Extract skill references from prompt"""
        return []


injector = SkillInjector()
