"""
Skill Parser - Parse SKILL.md frontmatter metadata and trigger keywords
"""

import re
from pathlib import Path
from typing import Optional


def parse_skill_md(skill_dir: Path) -> dict:
    """
    Parse SKILL.md, extract frontmatter metadata and trigger keywords

    Returns:
        {
            "name": str,
            "description": str,
            "triggers": [str, ...],   # List of trigger keywords
            "instruct": str,           # Full SKILL.md content
            "has_scripts": bool,       # Whether scripts/ directory exists
        }
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"name": skill_dir.name, "triggers": [], "instruct": ""}

    raw = skill_md.read_text(encoding="utf-8", errors="replace")

    # Extract frontmatter YAML
    name = skill_dir.name
    description = ""
    frontmatter_end = 0

    if raw.startswith("---"):
        end_match = re.search(r"^---\s*$", raw[3:], re.MULTILINE)
        if end_match:
            frontmatter_end = end_match.end() + 3
            frontmatter = raw[3:frontmatter_end - 3].strip()

            # Extract name
            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip().strip('"').strip("'")

            # Extract description/triggers
            desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
            if desc_match:
                description = desc_match.group(1).strip().strip('"').strip("'")

    # Content (everything after frontmatter)
    instruct = raw[frontmatter_end:].strip() if frontmatter_end > 0 else raw.strip()

    # Extract keywords from description
    triggers = extract_triggers(description, name)

    return {
        "name": name,
        "description": description,
        "triggers": triggers,
        "instruct": instruct,
        "has_scripts": (skill_dir / "scripts").exists(),
    }


def extract_triggers(description: str, fallback_name: str) -> list[str]:
    """
    Extract trigger keywords from description
    Strategy: phrases in quotes + file extensions + core verbs
    """
    triggers = []

    # Phrases in quotes
    quoted = re.findall(r'"([^"]+)"', description)
    for q in quoted:
        # Split quoted phrases into words
        words = [w.strip().lower() for w in q.replace(",", " ").split()]
        triggers.extend(w for w in words if len(w) > 2 and w not in triggers)

    # File extensions
    exts = re.findall(r'\.(\w+)["\s,.)]', description)
    for ext in exts:
        ext_clean = ext.lower()
        if f".{ext_clean}" not in triggers:
            triggers.append(f".{ext_clean}")

    # Core verbs/nouns (words starting with uppercase from description)
    cap_words = re.findall(r'\b([A-Z][a-z]+|[A-Z]{2,})\b', description)
    for cw in cap_words:
        cw_lower = cw.lower()
        if cw_lower not in triggers and len(cw) > 2:
            triggers.append(cw_lower)

    # Deduplicate + clean + sort by length
    cleaned = []
    for t in triggers:
        t = t.strip().strip("\\").strip(",").strip(".").strip('"').strip("'").strip()
        if t and len(t) > 2 and t not in cleaned:
            cleaned.append(t)
    cleaned.sort(key=len, reverse=True)
    cleaned.append(fallback_name.lower())

    return cleaned


def match_skills(user_message: str, skill_metas: list[dict], max_skills: int = 3) -> list[dict]:
    """
    Match user message with skill trigger keywords

    Returns:
        List of skill metadata sorted by match score [{name, triggers, instruct, ...}]
    """
    msg_lower = user_message.lower()
    scored = []

    for meta in skill_metas:
        score = 0
        for trigger in meta["triggers"]:
            if trigger in msg_lower:
                # Longer keyword matches get more points (more precise)
                score += len(trigger) * 2
            # Also match individual words
            for word in msg_lower.split():
                if trigger in word or word in trigger:
                    if len(word) > 2:
                        score += 1

        if score > 0:
            scored.append((score, meta))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:max_skills]]
