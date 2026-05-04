"""
Skills Registry - Manages agent skills
"""

from typing import Dict, Any, List, Callable


class SkillsRegistry:
    """Registry for agent skills"""

    def __init__(self):
        self.skills: Dict[str, Dict[str, Any]] = {}

    def register_skill(self, skill_id: str, skill_def: Dict[str, Any]):
        """Register a skill"""
        self.skills[skill_id] = skill_def

    def get_skill(self, skill_id: str) -> Dict[str, Any]:
        """Get skill definition"""
        return self.skills.get(skill_id, {})

    def list_skills(self) -> List[str]:
        """List all skill IDs"""
        return list(self.skills.keys())


skills_registry = SkillsRegistry()
