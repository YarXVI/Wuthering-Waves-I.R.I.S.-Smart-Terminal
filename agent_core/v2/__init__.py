"""
I.R.I.S. Agent Core v2

A production-ready agent framework built on onion architecture.

Architecture Layers:
  4. Interfaces: API / WebSocket / CLI endpoints
  3. Application: Use cases and service orchestration
  2. Domain: Core business logic and entity definitions
  1. Infrastructure: External adapters and protocol implementations

Core Capabilities:
  1. LCM (Lazy Context Materialization)
     - Chunk-based context storage with LRU caching
     - Sentinel detection for on-demand context loading
     - State machine driven context injection

  2. Chinese Thinking Skill
     - Native Chinese reasoning chain support
     - Metaphor and dialectical thinking enhancement
     - Content encoding integration with LCM protocol

  3. Skill Engine
     - Progressive disclosure level system
     - Automatic skill distillation from conversations
     - Feedback-driven skill evolution

  4. Personality System
     - Configurable agent personalities with traits and values
     - LLM parameter modulation per personality
     - Behavior boundary enforcement

Quick Start:
    from agent_core.v2 import AgentService, ProviderConfig, Chunk, LCMEngine

    service = AgentService()
    service.provider.register(ProviderConfig(
        name="default",
        model="gpt-4o",
        api_key="sk-...",
    ))

    service.lcm.store.add(Chunk(
        chunk_id="auth_handler",
        content="def login(): ...",
        summary="Authentication handler",
    ))

    result = await service.chat(
        agent_id="iris",
        user_message="Review the authentication handler",
    )
"""

# Domain - Core
from agent_core.v2.domain.execution_context import ExecutionContext
from agent_core.v2.domain.execution_result import ExecutionResult, ToolCallRecord
from agent_core.v2.domain.agent_runtime import AgentRuntime, RuntimeConfig
from agent_core.v2.domain.personality import Personality, PersonalityRegistry, PersonalityTrait, ValueStatement, BehaviorConfig, BoundaryRule

# Domain - Core Technologies
from agent_core.v2.domain.chinese_thinking import ChineseThinkingSkill, ThinkingConfig

# Infrastructure - Core
from agent_core.v2.infrastructure.provider_router import ProviderRouter, ProviderConfig
from agent_core.v2.infrastructure.memory_manager import MemoryManager, MemoryContext
from agent_core.v2.infrastructure.skill_engine import (
    SkillEngine, Skill, SkillResult,
    SkillLevel, SkillLevelDefinition, SkillInfo,
    Recommendation, EvolutionRecord, SkillFeedback,
    EvolutionStrategy, EvolutionStatus, SkillVersion,
    get_level_definition, get_all_level_definitions,
)

# Infrastructure - LCM (原生融合)
from agent_core.v2.infrastructure.chunk_store import ChunkStore, Chunk
from agent_core.v2.infrastructure.sentinel_detector import SentinelDetector, LoadRequest
from agent_core.v2.infrastructure.lcm_engine import LCMEngine, LCMConfig, LCMState, LCMEvent, LCMSession

# Application
from agent_core.v2.application.agent_service import AgentService

__version__ = "2.0.0"

__all__ = [
    # Domain - Core
    "ExecutionContext",
    "ExecutionResult",
    "ToolCallRecord",
    "AgentRuntime",
    "RuntimeConfig",
    # Domain - Personality
    "Personality",
    "PersonalityRegistry",
    "PersonalityTrait",
    "ValueStatement",
    "BehaviorConfig",
    "BoundaryRule",
    # Domain - Core Technologies
    "ChineseThinkingSkill",
    "ThinkingConfig",
    # Infrastructure - Core
    "ProviderRouter",
    "ProviderConfig",
    "MemoryManager",
    "MemoryContext",
    "SkillEngine",
    "Skill",
    "SkillResult",
    "SkillLevel",
    "SkillLevelDefinition",
    "SkillInfo",
    "Recommendation",
    "EvolutionRecord",
    "SkillFeedback",
    "EvolutionStrategy",
    "EvolutionStatus",
    "SkillVersion",
    "get_level_definition",
    "get_all_level_definitions",
    # Infrastructure - LCM
    "ChunkStore",
    "Chunk",
    "SentinelDetector",
    "LoadRequest",
    "LCMEngine",
    "LCMConfig",
    "LCMState",
    "LCMEvent",
    "LCMSession",
    # Application
    "AgentService",
]
