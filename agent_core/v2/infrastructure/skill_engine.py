"""Skill engine for loading, executing, and distilling skills."""

import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable


@dataclass
class Skill:
    """A skill definition."""

    id: str
    name: str
    description: str
    level: int = 1  # 1-5, higher = more advanced
    parameters: dict = field(default_factory=dict)
    prompt_template: str = ""
    tags: list[str] = field(default_factory=list)
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SkillResult:
    """Result of skill execution."""

    success: bool
    output: str
    skill_id: str
    level_used: int = 1
    error: Optional[str] = None


class SkillLevel(Enum):
    """技能等级 —— V1 渐进式披露等级系统"""
    LEVEL_0 = "level_0"  # 基础技能 - 随时可用
    LEVEL_1 = "level_1"  # 进阶技能 - 需要引导使用
    LEVEL_2 = "level_2"  # 高级技能 - 需要用户明确请求


@dataclass
class SkillLevelDefinition:
    """技能等级定义"""
    level: SkillLevel
    name: str
    description: str
    visibility: str  # always, contextual, explicit
    trust_required: float  # 0-1 所需信任度
    usage_count_required: int  # 所需使用次数

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level.value,
            "name": self.name,
            "description": self.description,
            "visibility": self.visibility,
            "trust_required": self.trust_required,
            "usage_count_required": self.usage_count_required,
        }


# 预定义的技能等级
SKILL_LEVEL_DEFINITIONS: Dict[SkillLevel, SkillLevelDefinition] = {
    SkillLevel.LEVEL_0: SkillLevelDefinition(
        level=SkillLevel.LEVEL_0,
        name="基础技能",
        description="随时可用的基础技能，无需特殊权限",
        visibility="always",
        trust_required=0.0,
        usage_count_required=0,
    ),
    SkillLevel.LEVEL_1: SkillLevelDefinition(
        level=SkillLevel.LEVEL_1,
        name="进阶技能",
        description="需要一定信任度和使用次数才能解锁的进阶技能",
        visibility="contextual",
        trust_required=0.3,
        usage_count_required=5,
    ),
    SkillLevel.LEVEL_2: SkillLevelDefinition(
        level=SkillLevel.LEVEL_2,
        name="高级技能",
        description="需要用户明确请求才能使用的高级技能",
        visibility="explicit",
        trust_required=0.7,
        usage_count_required=20,
    ),
}


def get_level_definition(level: SkillLevel) -> SkillLevelDefinition:
    """获取技能等级定义"""
    return SKILL_LEVEL_DEFINITIONS.get(level, SKILL_LEVEL_DEFINITIONS[SkillLevel.LEVEL_0])


def get_all_level_definitions() -> List[SkillLevelDefinition]:
    """获取所有技能等级定义"""
    return list(SKILL_LEVEL_DEFINITIONS.values())


@dataclass
class SkillInfo:
    """Skill information with level and category metadata."""
    skill_id: str
    name: str
    description: str
    level: SkillLevel
    category: str
    enabled: bool = True
    usage_count: int = 0
    last_used: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        level_def = get_level_definition(self.level)
        return {
            "skill_id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "level": self.level.value,
            "level_name": level_def.name,
            "category": self.category,
            "enabled": self.enabled,
            "usage_count": self.usage_count,
            "last_used": self.last_used,
            "metadata": self.metadata,
        }


@dataclass
class Recommendation:
    """Skill recommendation result with confidence scoring."""
    skill_id: str
    skill_name: str
    confidence: float  # 0-1
    reason: str
    context_keywords: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "skill_name": self.skill_name,
            "confidence": self.confidence,
            "reason": self.reason,
            "context_keywords": self.context_keywords,
        }


class EvolutionStrategy(Enum):
    """进化策略"""
    AUTO = "auto"
    FEEDBACK_DRIVEN = "feedback"
    USAGE_DRIVEN = "usage"
    COMBINED = "combined"


class EvolutionStatus(Enum):
    """进化状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class SkillVersion:
    """技能版本"""
    version_id: str
    skill_id: str
    version_number: int
    created_at: datetime
    changes: List[str]
    performance_score: float = 0.0
    usage_count: int = 0
    feedback_score: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version_id": self.version_id,
            "skill_id": self.skill_id,
            "version_number": self.version_number,
            "created_at": self.created_at.isoformat(),
            "changes": self.changes,
            "performance_score": self.performance_score,
            "usage_count": self.usage_count,
            "feedback_score": self.feedback_score,
        }


@dataclass
class EvolutionRecord:
    """进化记录"""
    record_id: str
    skill_id: str
    strategy: EvolutionStrategy
    status: EvolutionStatus
    previous_version: Optional[str]
    new_version: Optional[str]
    improvements: List[str]
    feedback: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "skill_id": self.skill_id,
            "strategy": self.strategy.value,
            "status": self.status.value,
            "previous_version": self.previous_version,
            "new_version": self.new_version,
            "improvements": self.improvements,
            "feedback": self.feedback,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SkillFeedback:
    """技能反馈"""
    feedback_id: str
    skill_id: str
    user_id: str
    rating: int  # 1-5
    comment: str
    improvement_suggestions: List[str]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "feedback_id": self.feedback_id,
            "skill_id": self.skill_id,
            "user_id": self.user_id,
            "rating": self.rating,
            "comment": self.comment,
            "improvement_suggestions": self.improvement_suggestions,
            "created_at": self.created_at.isoformat(),
        }


class SkillEngine:
    """Manages skill lifecycle: load, execute, distill, evolve.

    Unified skill engine with progressive disclosure levels,
    recommendation system, and feedback-driven evolution.
    """

    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or Path.home() / ".iris" / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)
        self._skills: dict[str, Skill] = {}
        self._skill_infos: dict[str, SkillInfo] = {}
        self._skill_categories: Dict[str, List[str]] = {}
        self._keyword_index: Dict[str, List[str]] = {}
        self._skill_versions: Dict[str, List[SkillVersion]] = {}
        self._evolution_records: List[EvolutionRecord] = []
        self._feedback_records: Dict[str, List[SkillFeedback]] = {}
        self._evolution_strategy: EvolutionStrategy = EvolutionStrategy.COMBINED
        self._min_feedback_score: float = 2.5
        self._min_usage_threshold: int = 10
        self._load_builtin_skills()

    def _load_builtin_skills(self) -> None:
        """Load built-in skills."""
        builtins = [
            Skill(
                id="summarize",
                name="Summarize Text",
                description="Summarize long text into key points",
                level=1,
                parameters={"text": "", "max_points": 3},
                prompt_template=(
                    "Summarize the following text into {max_points} key points:\n\n{text}\n\n"
                    "Key points:"
                ),
                tags=["builtin", "text"],
            ),
            Skill(
                id="translate",
                name="Translate Text",
                description="Translate text between languages",
                level=1,
                parameters={"text": "", "target_language": "English"},
                prompt_template=(
                    "Translate the following text to {target_language}:\n\n{text}\n\n"
                    "Translation:"
                ),
                tags=["builtin", "text"],
            ),
            Skill(
                id="code_review",
                name="Code Review",
                description="Review code for issues and improvements",
                level=2,
                parameters={"code": "", "language": "python"},
                prompt_template=(
                    "Review the following {language} code for bugs, style issues, "
                    "and improvements:\n\n```{language}\n{code}\n```\n\n"
                    "Review:"
                ),
                tags=["builtin", "code"],
            ),
        ]
        for skill in builtins:
            self._skills[skill.id] = skill
            self._register_skill_info(skill)

    def _register_skill_info(self, skill: Skill, category: str = "general") -> None:
        """Register skill metadata for indexing and recommendation."""
        level = SkillLevel.LEVEL_0 if skill.level <= 1 else SkillLevel.LEVEL_1 if skill.level <= 3 else SkillLevel.LEVEL_2
        skill_info = SkillInfo(
            skill_id=skill.id,
            name=skill.name,
            description=skill.description,
            level=level,
            category=category,
            enabled=True,
            usage_count=skill.usage_count,
            metadata={"tags": skill.tags, "parameters": skill.parameters},
        )
        self._skill_infos[skill.id] = skill_info

        # 更新类别索引
        if category not in self._skill_categories:
            self._skill_categories[category] = []
        if skill.id not in self._skill_categories[category]:
            self._skill_categories[category].append(skill.id)

    # ========== V2 基础 API ==========

    async def load(self, skill_id: str) -> Optional[Skill]:
        """Load a skill by ID."""
        if skill_id in self._skills:
            return self._skills[skill_id]

        skill_file = self.skills_dir / f"{skill_id}.json"
        if skill_file.exists():
            with open(skill_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            skill = Skill(**data)
            self._skills[skill_id] = skill
            self._register_skill_info(skill)
            return skill

        return None

    async def list_skills(self, tag: Optional[str] = None) -> list[Skill]:
        """List all skills, optionally filtered by tag."""
        skills = list(self._skills.values())
        if tag:
            skills = [s for s in skills if tag in s.tags]
        return skills

    async def execute(self, skill_id: str, params: dict, user_level: int = 5) -> SkillResult:
        """Execute a skill with progressive disclosure."""
        skill = await self.load(skill_id)
        if not skill:
            return SkillResult(success=False, output=f"Skill '{skill_id}' not found", skill_id=skill_id)

        effective_level = min(skill.level, user_level)

        try:
            prompt = skill.prompt_template.format(**{**skill.parameters, **params})
        except KeyError as e:
            return SkillResult(success=False, output=f"Missing parameter: {e}", skill_id=skill_id)

        skill.usage_count += 1
        if skill_id in self._skill_infos:
            self._skill_infos[skill_id].usage_count += 1
            self._skill_infos[skill_id].last_used = datetime.now().isoformat()

        return SkillResult(
            success=True,
            output=prompt,
            skill_id=skill_id,
            level_used=effective_level,
        )

    async def distill(self, task_description: str, conversation: list[dict], success: bool = True) -> Optional[Skill]:
        """Auto-distill a skill from a successful conversation."""
        if not success or len(conversation) < 4:
            return None

        tool_calls = sum(1 for m in conversation if m.get("tool_calls"))
        if tool_calls < 2:
            return None

        skill_id = f"auto_{hashlib.md5(task_description.encode()).hexdigest()[:8]}"
        params = self._extract_params(conversation)

        skill = Skill(
            id=skill_id,
            name=f"Auto: {task_description[:30]}",
            description=task_description,
            level=2,
            parameters=params,
            prompt_template=self._generate_template(conversation),
            tags=["auto-distilled"],
        )

        await self._save_skill(skill)
        self._skills[skill_id] = skill
        self._register_skill_info(skill, category="auto")
        return skill

    # ========== Skill Pool API ==========

    def add_skill(self, skill_info: SkillInfo):
        """Add skill metadata to the registry."""
        self._skill_infos[skill_info.skill_id] = skill_info

        if skill_info.category not in self._skill_categories:
            self._skill_categories[skill_info.category] = []
        if skill_info.skill_id not in self._skill_categories[skill_info.category]:
            self._skill_categories[skill_info.category].append(skill_info.skill_id)

    def remove_skill(self, skill_id: str):
        """Remove skill from registry."""
        if skill_id in self._skill_infos:
            skill = self._skill_infos[skill_id]
            if skill.category in self._skill_categories:
                self._skill_categories[skill.category].remove(skill_id)
            del self._skill_infos[skill_id]
        if skill_id in self._skills:
            del self._skills[skill_id]

    def get_skill_info(self, skill_id: str) -> Optional[SkillInfo]:
        """Get skill metadata by ID."""
        return self._skill_infos.get(skill_id)

    def get_all_skill_infos(self) -> List[SkillInfo]:
        """List all skill metadata."""
        return list(self._skill_infos.values())

    def get_skills_by_level(self, level: SkillLevel) -> List[SkillInfo]:
        """Filter skills by level."""
        return [s for s in self._skill_infos.values() if s.level == level]

    def get_skills_by_category(self, category: str) -> List[SkillInfo]:
        """Filter skills by category."""
        skill_ids = self._skill_categories.get(category, [])
        return [self._skill_infos.get(id) for id in skill_ids if self._skill_infos.get(id)]

    def get_categories(self) -> List[str]:
        """List all categories."""
        return list(self._skill_categories.keys())

    def enable_skill(self, skill_id: str):
        """Enable a skill."""
        if skill_id in self._skill_infos:
            self._skill_infos[skill_id].enabled = True

    def disable_skill(self, skill_id: str):
        """Disable a skill."""
        if skill_id in self._skill_infos:
            self._skill_infos[skill_id].enabled = False

    def get_enabled_skills(self) -> List[SkillInfo]:
        """List all enabled skills."""
        return [s for s in self._skill_infos.values() if s.enabled]

    def get_visible_skills(self, trust_level: float, usage_count: int) -> List[SkillInfo]:
        """List skills visible to user based on trust and usage."""
        visible = []
        for skill in self.get_enabled_skills():
            level_def = get_level_definition(skill.level)
            if trust_level >= level_def.trust_required and usage_count >= level_def.usage_count_required:
                visible.append(skill)
        return visible

    def get_stats(self) -> Dict[str, Any]:
        """Get skill registry statistics."""
        total = len(self._skill_infos)
        enabled = len(self.get_enabled_skills())
        level_counts = {level.value: len(self.get_skills_by_level(level)) for level in SkillLevel}
        return {
            "total_skills": total,
            "enabled_skills": enabled,
            "disabled_skills": total - enabled,
            "level_counts": level_counts,
            "categories": self.get_categories(),
        }

    # ========== Recommender API ==========

    def build_index(self):
        """Build keyword index for skill matching."""
        self._keyword_index = {}
        for skill in self.get_enabled_skills():
            keywords = self._extract_keywords(skill)
            for keyword in keywords:
                keyword = keyword.lower()
                if keyword not in self._keyword_index:
                    self._keyword_index[keyword] = []
                if skill.skill_id not in self._keyword_index[keyword]:
                    self._keyword_index[keyword].append(skill.skill_id)

    def _extract_keywords(self, skill: SkillInfo) -> List[str]:
        """Extract keywords from skill metadata."""
        keywords = []
        keywords.extend(skill.name.lower().split())
        keywords.extend(skill.description.lower().split())
        keywords.append(skill.category.lower())
        if 'keywords' in skill.metadata:
            keywords.extend([k.lower() for k in skill.metadata['keywords']])
        return list(set(keywords))

    def recommend(self, context: str, trust_level: float = 0.0,
                  usage_count: int = 0, limit: int = 5) -> List[Recommendation]:
        """Recommend skills based on context."""
        recommendations = []
        visible_skills = self.get_visible_skills(trust_level, usage_count)
        if not visible_skills:
            return recommendations

        context_keywords = [k.lower() for k in context.split() if len(k) > 2]

        for skill in visible_skills:
            confidence = self._calculate_confidence(skill, context_keywords)
            if confidence > 0.1:
                reason = self._generate_reason(skill, context_keywords)
                recommendations.append(Recommendation(
                    skill_id=skill.skill_id,
                    skill_name=skill.name,
                    confidence=confidence,
                    reason=reason,
                    context_keywords=context_keywords[:5]
                ))

        recommendations.sort(key=lambda r: r.confidence, reverse=True)
        return recommendations[:limit]

    def _calculate_confidence(self, skill: SkillInfo, context_keywords: List[str]) -> float:
        """Calculate match confidence between skill and context."""
        if not context_keywords:
            return 0.0
        skill_keywords = self._extract_keywords(skill)
        matched = sum(1 for kw in context_keywords if kw in skill_keywords)
        base_score = matched / len(context_keywords) if context_keywords else 0.0
        usage_bonus = min(skill.usage_count / 100, 0.2)
        level_bonus = {
            SkillLevel.LEVEL_0: 0.1,
            SkillLevel.LEVEL_1: 0.05,
            SkillLevel.LEVEL_2: 0.0,
        }.get(skill.level, 0.0)
        return min(base_score + usage_bonus + level_bonus, 1.0)

    def _generate_reason(self, skill: SkillInfo, context_keywords: List[str]) -> str:
        """Generate human-readable recommendation reason."""
        skill_keywords = self._extract_keywords(skill)
        matched_keywords = [kw for kw in context_keywords if kw in skill_keywords]
        if matched_keywords:
            return f"Matched keywords: {', '.join(matched_keywords)}"
        return "Recommended based on usage history and context"

    # ========== Evolution API ==========

    def add_version(self, skill_id: str, changes: List[str]) -> SkillVersion:
        """Add a new skill version."""
        versions = self._skill_versions.get(skill_id, [])
        version_number = len(versions) + 1
        version_id = f"{skill_id}_v{version_number}"

        version = SkillVersion(
            version_id=version_id,
            skill_id=skill_id,
            version_number=version_number,
            created_at=datetime.now(),
            changes=changes
        )

        if skill_id not in self._skill_versions:
            self._skill_versions[skill_id] = []
        self._skill_versions[skill_id].append(version)
        return version

    def get_versions(self, skill_id: str) -> List[SkillVersion]:
        """Get all versions of a skill."""
        return self._skill_versions.get(skill_id, [])

    def get_latest_version(self, skill_id: str) -> Optional[SkillVersion]:
        """Get the latest version of a skill."""
        versions = self._skill_versions.get(skill_id, [])
        return versions[-1] if versions else None

    def add_feedback(self, feedback: SkillFeedback):
        """Add feedback for a skill."""
        if feedback.skill_id not in self._feedback_records:
            self._feedback_records[feedback.skill_id] = []
        self._feedback_records[feedback.skill_id].append(feedback)

    def get_feedback(self, skill_id: str) -> List[SkillFeedback]:
        """Get all feedback for a skill."""
        return self._feedback_records.get(skill_id, [])

    def calculate_feedback_score(self, skill_id: str) -> float:
        """Calculate average feedback score."""
        feedbacks = self.get_feedback(skill_id)
        if not feedbacks:
            return 0.0
        return sum(f.rating for f in feedbacks) / len(feedbacks)

    async def evaluate_skill(self, skill_info: SkillInfo) -> Dict[str, Any]:
        """Evaluate if a skill needs evolution."""
        feedback_score = self.calculate_feedback_score(skill_info.skill_id)
        usage_count = skill_info.usage_count
        latest_version = self.get_latest_version(skill_info.skill_id)

        needs_evolution = False
        reasons = []

        if feedback_score > 0 and feedback_score < self._min_feedback_score:
            needs_evolution = True
            reasons.append(f"Low feedback score ({feedback_score}/5)")

        if usage_count >= self._min_usage_threshold:
            needs_evolution = True
            reasons.append(f"Usage threshold reached ({usage_count})")

        if latest_version:
            days_since_update = (datetime.now() - latest_version.created_at).days
            if days_since_update > 30:
                needs_evolution = True
                reasons.append(f"Version stale ({days_since_update} days)")

        return {
            "skill_id": skill_info.skill_id,
            "needs_evolution": needs_evolution,
            "reasons": reasons,
            "feedback_score": feedback_score,
            "usage_count": usage_count,
            "current_version": latest_version.version_number if latest_version else 0
        }

    async def evolve_skill(self, skill_info: SkillInfo) -> EvolutionRecord:
        """Evolve a skill based on feedback and usage."""
        record_id = f"evo_{datetime.now().timestamp()}"
        previous_version = self.get_latest_version(skill_info.skill_id)
        previous_version_id = previous_version.version_id if previous_version else None

        record = EvolutionRecord(
            record_id=record_id,
            skill_id=skill_info.skill_id,
            strategy=self._evolution_strategy,
            status=EvolutionStatus.IN_PROGRESS,
            previous_version=previous_version_id,
            new_version=None,
            improvements=[]
        )

        try:
            improvements = await self._perform_evolution(skill_info)
            new_version = self.add_version(skill_info.skill_id, improvements)
            record.new_version = new_version.version_id
            record.improvements = improvements
            record.status = EvolutionStatus.COMPLETED
            self._evolution_records.append(record)
            return record

        except Exception as e:
            record.status = EvolutionStatus.FAILED
            record.feedback = str(e)
            self._evolution_records.append(record)
            raise

    async def _perform_evolution(self, skill_info: SkillInfo) -> List[str]:
        """Perform actual evolution operations."""
        improvements = []
        feedbacks = self.get_feedback(skill_info.skill_id)
        for feedback in feedbacks:
            if feedback.improvement_suggestions:
                improvements.extend(feedback.improvement_suggestions)
        if not improvements:
            improvements.append("Auto-optimized from usage data")
            improvements.append("Performance optimization")
        return list(set(improvements))

    def get_evolution_history(self, skill_id: Optional[str] = None) -> List[EvolutionRecord]:
        """Get evolution history for a skill."""
        if skill_id:
            return [r for r in self._evolution_records if r.skill_id == skill_id]
        return self._evolution_records

    def get_pending_evolutions(self) -> List[str]:
        """List skills pending evolution."""
        pending = []
        for skill_id, versions in self._skill_versions.items():
            latest = versions[-1] if versions else None
            if latest:
                days_old = (datetime.now() - latest.created_at).days
                feedback_score = self.calculate_feedback_score(skill_id)
                if days_old > 30 or (feedback_score > 0 and feedback_score < self._min_feedback_score):
                    pending.append(skill_id)
        return pending

    # ========== Skill Parser API ==========

    def parse_skill_md(self, skill_dir: Path) -> dict:
        """Parse SKILL.md frontmatter metadata and trigger keywords"""
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            return {"name": skill_dir.name, "triggers": [], "instruct": ""}

        raw = skill_md.read_text(encoding="utf-8", errors="replace")

        name = skill_dir.name
        description = ""
        frontmatter_end = 0

        if raw.startswith("---"):
            end_match = re.search(r"^---\s*$", raw[3:], re.MULTILINE)
            if end_match:
                frontmatter_end = end_match.end() + 3
                frontmatter = raw[3:frontmatter_end - 3].strip()

                name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
                if name_match:
                    name = name_match.group(1).strip().strip('"').strip("'")

                desc_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
                if desc_match:
                    description = desc_match.group(1).strip().strip('"').strip("'")

        instruct = raw[frontmatter_end:].strip() if frontmatter_end > 0 else raw.strip()
        triggers = self._extract_triggers(description, name)

        return {
            "name": name,
            "description": description,
            "triggers": triggers,
            "instruct": instruct,
            "has_scripts": (skill_dir / "scripts").exists(),
        }

    def _extract_triggers(self, description: str, fallback_name: str) -> list[str]:
        """Extract trigger keywords from description"""
        triggers = []

        quoted = re.findall(r'"([^"]+)"', description)
        for q in quoted:
            words = [w.strip().lower() for w in q.replace(",", " ").split()]
            triggers.extend(w for w in words if len(w) > 2 and w not in triggers)

        exts = re.findall(r'\.(\w+)["\s,.)]', description)
        for ext in exts:
            ext_clean = ext.lower()
            if f".{ext_clean}" not in triggers:
                triggers.append(f".{ext_clean}")

        cap_words = re.findall(r'\b([A-Z][a-z]+|[A-Z]{2,})\b', description)
        for cw in cap_words:
            cw_lower = cw.lower()
            if cw_lower not in triggers and len(cw) > 2:
                triggers.append(cw_lower)

        cleaned = []
        for t in triggers:
            t = t.strip().strip("\\").strip(",").strip(".").strip('"').strip("'").strip()
            if t and len(t) > 2 and t not in cleaned:
                cleaned.append(t)
        cleaned.sort(key=len, reverse=True)
        cleaned.append(fallback_name.lower())

        return cleaned

    def match_skills(self, user_message: str, skill_metas: list[dict], max_skills: int = 3) -> list[dict]:
        """Match user message with skill trigger keywords"""
        msg_lower = user_message.lower()
        scored = []

        for meta in skill_metas:
            score = 0
            for trigger in meta["triggers"]:
                if trigger in msg_lower:
                    score += len(trigger) * 2
                for word in msg_lower.split():
                    if trigger in word or word in trigger:
                        if len(word) > 2:
                            score += 1

            if score > 0:
                scored.append((score, meta))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:max_skills]]

    # ========== Persistence ==========

    def _extract_params(self, conversation: list[dict]) -> dict:
        """Extract potential parameters from conversation."""
        params = {}
        for msg in conversation:
            content = msg.get("content", "")
            if "=" in content:
                for part in content.split():
                    if "=" in part:
                        k, v = part.split("=", 1)
                        params[k.strip()] = v.strip()
        return params

    def _generate_template(self, conversation: list[dict]) -> str:
        """Generate a prompt template from conversation."""
        for msg in conversation:
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""

    async def _save_skill(self, skill: Skill) -> None:
        """Save skill to disk."""
        skill_file = self.skills_dir / f"{skill.id}.json"
        with open(skill_file, "w", encoding="utf-8") as f:
            json.dump({
                "id": skill.id,
                "name": skill.name,
                "description": skill.description,
                "level": skill.level,
                "parameters": skill.parameters,
                "prompt_template": skill.prompt_template,
                "tags": skill.tags,
                "usage_count": skill.usage_count,
                "created_at": skill.created_at.isoformat(),
            }, f, ensure_ascii=False, indent=2)

    async def save_evolution_data(self, filepath: str):
        """Save evolution data to file."""
        data = {
            "versions": {
                skill_id: [v.to_dict() for v in versions]
                for skill_id, versions in self._skill_versions.items()
            },
            "evolution_records": [r.to_dict() for r in self._evolution_records],
            "feedback_records": {
                skill_id: [f.to_dict() for f in feedbacks]
                for skill_id, feedbacks in self._feedback_records.items()
            },
            "strategy": self._evolution_strategy.value,
            "min_feedback_score": self._min_feedback_score,
            "min_usage_threshold": self._min_usage_threshold,
        }
        Path(filepath).write_text(json.dumps(data, ensure_ascii=False, indent=2))

    async def load_evolution_data(self, filepath: str):
        """Load evolution data from file."""
        if not Path(filepath).exists():
            return

        try:
            data = json.loads(Path(filepath).read_text(encoding='utf-8'))

            for skill_id, versions_data in data.get("versions", {}).items():
                versions = []
                for v_data in versions_data:
                    version = SkillVersion(
                        version_id=v_data["version_id"],
                        skill_id=v_data["skill_id"],
                        version_number=v_data["version_number"],
                        created_at=datetime.fromisoformat(v_data["created_at"]),
                        changes=v_data["changes"],
                        performance_score=v_data.get("performance_score", 0.0),
                        usage_count=v_data.get("usage_count", 0),
                        feedback_score=v_data.get("feedback_score", 0.0)
                    )
                    versions.append(version)
                self._skill_versions[skill_id] = versions

            for record_data in data.get("evolution_records", []):
                record = EvolutionRecord(
                    record_id=record_data["record_id"],
                    skill_id=record_data["skill_id"],
                    strategy=EvolutionStrategy(record_data["strategy"]),
                    status=EvolutionStatus(record_data["status"]),
                    previous_version=record_data.get("previous_version"),
                    new_version=record_data.get("new_version"),
                    improvements=record_data.get("improvements", []),
                    feedback=record_data.get("feedback", ""),
                    created_at=datetime.fromisoformat(record_data["created_at"])
                )
                self._evolution_records.append(record)

            for skill_id, feedbacks_data in data.get("feedback_records", {}).items():
                feedbacks = []
                for f_data in feedbacks_data:
                    feedback = SkillFeedback(
                        feedback_id=f_data["feedback_id"],
                        skill_id=f_data["skill_id"],
                        user_id=f_data["user_id"],
                        rating=f_data["rating"],
                        comment=f_data["comment"],
                        improvement_suggestions=f_data.get("improvement_suggestions", []),
                        created_at=datetime.fromisoformat(f_data["created_at"])
                    )
                    feedbacks.append(feedback)
                self._feedback_records[skill_id] = feedbacks

            if "strategy" in data:
                self._evolution_strategy = EvolutionStrategy(data["strategy"])
            if "min_feedback_score" in data:
                self._min_feedback_score = data["min_feedback_score"]
            if "min_usage_threshold" in data:
                self._min_usage_threshold = data["min_usage_threshold"]

        except Exception:
            pass


# ========== Global Instance ==========

_skill_engine: Optional[SkillEngine] = None


def get_skill_engine() -> SkillEngine:
    """获取全局技能引擎"""
    global _skill_engine
    if _skill_engine is None:
        _skill_engine = SkillEngine()
    return _skill_engine
