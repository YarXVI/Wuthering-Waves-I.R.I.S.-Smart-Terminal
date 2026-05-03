"""
Skill Parser �?解析 SKILL.md 前件元数�?+ 触发关键�?
"""

import re
from pathlib import Path
from typing import Optional


def parse_skill_md(skill_dir: Path) -> dict:
    """
    解析 SKILL.md，提取前件元数据和触发关键词�?

    返回:
        {
            "name": str,
            "description": str,
            "triggers": [str, ...],   # 触发关键词列�?
            "instruct": str,           # 完整�?SKILL.md 正文
            "has_scripts": bool,       # 是否�?scripts/ 目录
        }
    """
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return {"name": skill_dir.name, "triggers": [], "instruct": ""}

    raw = skill_md.read_text(encoding="utf-8", errors="replace")

    # 提取前件 YAML
    name = skill_dir.name
    description = ""
    frontmatter_end = 0

    if raw.startswith("---"):
        end_match = re.search(r"^---\s*$", raw[3:], re.MULTILINE)
        if end_match:
            frontmatter_end = end_match.end() + 3
            frontmatter = raw[3:frontmatter_end - 3].strip()

            # 提取 name
            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            if name_match:
                name = name_match.group(1).strip().strip('"').strip("'")

            # 提取 description/triggers
            desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
            if desc_match:
                description = desc_match.group(1).strip().strip('"').strip("'")

    # 正文（前件之后的所有内容）
    instruct = raw[frontmatter_end:].strip() if frontmatter_end > 0 else raw.strip()

    # �?description 中提取关键词
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
    �?description 中提取触发关键词�?
    策略：取引号内的短语 + 文件扩展�?+ 核心动词
    """
    triggers = []

    # 引号内的短语
    quoted = re.findall(r'"([^"]+)"', description)
    for q in quoted:
        # 把引号短语拆成词
        words = [w.strip().lower() for w in q.replace(",", " ").split()]
        triggers.extend(w for w in words if len(w) > 2 and w not in triggers)

    # 文件扩展�?
    exts = re.findall(r'\.(\w+)["\s,.)]', description)
    for ext in exts:
        ext_clean = ext.lower()
        if f".{ext_clean}" not in triggers:
            triggers.append(f".{ext_clean}")

    # 核心动词/名词（从 description 中以大写开头的词）
    cap_words = re.findall(r'\b([A-Z][a-z]+|[A-Z]{2,})\b', description)
    for cw in cap_words:
        cw_lower = cw.lower()
        if cw_lower not in triggers and len(cw) > 2:
            triggers.append(cw_lower)

    # 去重 + 清理 + 按长度排�?
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
    将用户消息与技能触发关键词匹配�?

    返回:
        按匹配度排序的技能元数据列表 [{name, triggers, instruct, ...}]
    """
    msg_lower = user_message.lower()
    scored = []

    for meta in skill_metas:
        score = 0
        for trigger in meta["triggers"]:
            if trigger in msg_lower:
                # 长关键词匹配加分更多（更精确�?
                score += len(trigger) * 2
            # 也匹配单独的�?
            for word in msg_lower.split():
                if trigger in word or word in trigger:
                    if len(word) > 2:
                        score += 1

        if score > 0:
            scored.append((score, meta))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:max_skills]]
