"""
Meeting Templates - Predefined meeting templates
"""

from typing import Dict, List


DEFAULT_TEMPLATES = [
    {
        "id": "brainstorm",
        "name": "Brainstorm Meeting",
        "description": "For creative idea generation",
        "rounds": 3,
    },
    {
        "id": "standup",
        "name": "Daily Standup",
        "description": "Quick daily sync",
        "rounds": 1,
    },
    {
        "id": "review",
        "name": "Code Review",
        "description": "Review code changes",
        "rounds": 2,
    },
]


def get_templates() -> List[Dict]:
    """Get all meeting templates"""
    return DEFAULT_TEMPLATES


def get_template(template_id: str) -> Dict:
    """Get template by ID"""
    for template in DEFAULT_TEMPLATES:
        if template["id"] == template_id:
            return template
    return {}


def create_template(name: str, description: str, suggested_agents: List[str], default_rounds: int = 6) -> Dict:
    """Create a new meeting template"""
    new_template = {
        "id": name.lower().replace(" ", "-"),
        "name": name,
        "description": description,
        "suggested_agents": suggested_agents,
        "rounds": default_rounds,
    }
    DEFAULT_TEMPLATES.append(new_template)
    return new_template


def create_from_template(template_id: str, topic: str) -> Dict:
    """Create meeting from template"""
    template = get_template(template_id)
    if not template:
        return {}
    
    return {
        "topic": topic,
        "template_id": template_id,
        "rounds": template.get("rounds", 6),
        "suggested_agents": template.get("suggested_agents", []),
    }
