"""Application layer service for agent operations."""

from typing import Optional

from agent_core.v2.domain.execution_context import ExecutionContext
from agent_core.v2.domain.execution_result import ExecutionResult
from agent_core.v2.domain.agent_runtime import AgentRuntime, RuntimeConfig
from agent_core.v2.infrastructure.provider_router import ProviderRouter
from agent_core.v2.infrastructure.memory_manager import MemoryManager
from agent_core.v2.infrastructure.skill_engine import SkillEngine
from agent_core.v2.infrastructure.lcm_engine import LCMEngine, LCMConfig


class AgentService:
    """
    High-level service for agent operations.
    Provides a clean API for the interface layer (routers, WebSocket handlers).

    Integrated with LCM (Lazy Context Materialization):
    - service.lcm.store.add(Chunk(...))
    - service.lcm.build_system_prompt(base_prompt)
    """

    def __init__(
        self,
        provider_router: Optional[ProviderRouter] = None,
        memory_manager: Optional[MemoryManager] = None,
        skill_engine: Optional[SkillEngine] = None,
        lcm_engine: Optional[LCMEngine] = None,
        runtime_config: Optional[RuntimeConfig] = None,
    ):
        self.provider = provider_router or ProviderRouter()
        self.memory = memory_manager or MemoryManager()
        self.skills = skill_engine or SkillEngine()
        self.lcm = lcm_engine or LCMEngine()
        self.runtime = AgentRuntime(
            provider_router=self.provider,
            memory_manager=self.memory,
            skill_engine=self.skills,
            lcm_engine=self.lcm,
            config=runtime_config,
        )
        self._agents: dict[str, dict] = {}  # Simple agent registry

    def register_agent(self, agent_id: str, config: dict) -> None:
        """Register an agent configuration."""
        self._agents[agent_id] = {
            "id": agent_id,
            **config,
        }

    def list_agents(self) -> list[dict]:
        """List all registered agents."""
        return list(self._agents.values())

    def get_agent(self, agent_id: str) -> Optional[dict]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)

    async def chat(
        self,
        agent_id: str,
        user_message: str,
        user_id: str = "default",
        room_id: Optional[str] = None,
    ) -> ExecutionResult:
        """Simple chat with an agent."""
        if not agent_id:
            raise ValueError("agent_id is required")
        if not user_message:
            raise ValueError("user_message is required")

        context = ExecutionContext(
            agent_id=agent_id,
            user_id=user_id,
            room_id=room_id,
            task_type="chat",
        )

        return await self.runtime.run(context, user_message)

    async def execute_skill(
        self,
        skill_id: str,
        params: dict,
        user_level: int = 5,
    ) -> dict:
        """Execute a skill directly."""
        result = await self.skills.execute(skill_id, params, user_level)
        return {
            "success": result.success,
            "output": result.output,
            "skill_id": result.skill_id,
            "level_used": result.level_used,
            "error": result.error,
        }

    async def get_memory(self, agent_id: str, user_id: str = "default") -> dict:
        """Get agent memory context."""
        memory = await self.memory.load(agent_id, user_id)
        return {
            "working": memory.working,
            "short_term_count": len(memory.short_term),
            "long_term_count": len(memory.long_term),
            "user_profile": memory.user_profile,
        }
