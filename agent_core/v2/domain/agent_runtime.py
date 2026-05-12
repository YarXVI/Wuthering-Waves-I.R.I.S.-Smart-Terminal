"""Agent runtime with ReAct loop and core technologies."""

import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

from agent_core.v2.domain.execution_context import ExecutionContext
from agent_core.v2.domain.execution_result import ExecutionResult, ToolCallRecord
from agent_core.v2.domain.chinese_thinking import ChineseThinkingSkill, ThinkingConfig
from agent_core.v2.domain.personality import Personality, PersonalityRegistry
from agent_core.v2.infrastructure.provider_router import ProviderRouter
from agent_core.v2.infrastructure.memory_manager import MemoryManager, MemoryContext
from agent_core.v2.infrastructure.skill_engine import SkillEngine, SkillLevel, SkillInfo
from agent_core.v2.infrastructure.lcm_engine import LCMEngine, LCMConfig
from agent_core.v2.infrastructure.content_encoding import EncodingType, ContentEncodingRegistry
from agent_core.v2.domain.chinese_thinking import ChineseThinkEncoding


@dataclass
class RuntimeConfig:
    """Configuration for agent runtime."""

    max_steps: int = 10
    temperature: float = 0.7
    max_tokens_per_step: int = 4096
    enable_memory: bool = True
    enable_skills: bool = True
    enable_skill_distillation: bool = True

    # LCM 配置
    enable_lcm: bool = True
    lcm_config: Optional[LCMConfig] = None

    # 中文思考技能配置
    enable_chinese_thinking: bool = True
    chinese_thinking_depth: str = "deep"
    preserve_thinking_chain: bool = True

    # 人格配置
    personality_id: str = "iris"
    enable_personality: bool = True

    system_prompt_template: str = (
        "You are {agent_name}, an AI assistant.\n"
        "Current user: {user_id}\n"
        "Session: {session_id}\n"
        "Task type: {task_type}\n"
        "{personality_context}"
        "{memory_context}"
    )


class AgentRuntime:
    """
    Unified Agent execution runtime with core technologies.

    Core Technologies:
      1. LCM (Lazy Context Materialization) —— 惰性上下文协议
         - 通过 LCMEngine 实现完整的 chunk 存储、哨兵检测、状态机
         - 与 v2.infrastructure.lcm_engine 深度集成

      2. 中文思考技能 (Chinese Thinking Skill)
         - 内部推理使用中文
         - 结构化思考链
         - 隐喻与辩证思维增强

    ReAct loop:
      1. Load memory
      2. Build system prompt (with LCM instructions if enabled)
      3. Apply Chinese Thinking if enabled
      4. Build messages with tool definitions
      5. Call LLM via ProviderRouter
      6. If LCM enabled: detect sentinel -> load chunk -> inject -> continue
      7. If tool calls -> execute tools -> append results
      8. If final answer -> extract thinking chain -> return result
      9. Auto-distill skill from successful runs
    """

    def __init__(
        self,
        provider_router: ProviderRouter,
        memory_manager: MemoryManager,
        skill_engine: SkillEngine,
        lcm_engine: Optional[LCMEngine] = None,
        personality_registry: Optional[PersonalityRegistry] = None,
        config: Optional[RuntimeConfig] = None,
    ):
        self.provider = provider_router
        self.memory = memory_manager
        self.skills = skill_engine
        self.lcm = lcm_engine
        self.config = config or RuntimeConfig()
        self._tool_registry: dict[str, Callable] = {}

        # 初始化人格系统
        if self.config.enable_personality:
            self._personality_registry = personality_registry or PersonalityRegistry()
            self._personality = self._personality_registry.get(self.config.personality_id)
        else:
            self._personality_registry = None
            self._personality = None

        # 初始化 LCM（含内容编码）
        if self.config.enable_lcm and self.lcm is None:
            lcm_config = self.config.lcm_config or LCMConfig()
            self.lcm = LCMEngine(config=lcm_config)

            # 如果启用中文思考，注册中文思考编码到 LCM
            if self.config.enable_chinese_thinking:
                self.lcm.register_encoding(ChineseThinkEncoding(
                    skill=self._chinese_thinking
                ))
                self.lcm.set_encoding(EncodingType.CHINESE_THINK)

        # 中文思考技能
        if self.config.enable_chinese_thinking:
            self._chinese_thinking = ChineseThinkingSkill(
                config=ThinkingConfig(
                    enable_chinese_thinking=True,
                    thinking_language="zh",
                    thinking_depth=self.config.chinese_thinking_depth,
                    preserve_thinking_chain=self.config.preserve_thinking_chain,
                    enable_metaphor=True,
                    enable_dialectical=True,
                )
            )
        else:
            self._chinese_thinking = None

    def register_tool(self, name: str, func: Callable) -> None:
        """Register a tool for the agent to use."""
        self._tool_registry[name] = func

    def _build_system_prompt(self, context: ExecutionContext, memory: MemoryContext) -> str:
        """Build system prompt with personality, memory context, and skill recommendations."""
        # 人格上下文
        personality_text = ""
        if self._personality:
            personality_text = f"\n{self._personality.generate_system_prompt()}"

        # 记忆上下文
        memory_text = ""
        if memory.working:
            memory_text += f"\nWorking memory: {memory.working}"
        if memory.short_term:
            memory_text += f"\nRecent context: {memory.short_term[-3:]}"
        if memory.user_profile:
            memory_text += f"\nUser profile: {memory.user_profile}"

        # 技能推荐上下文
        skill_text = ""
        if self.config.enable_skills:
            recommendations = self.skills.recommend(
                context=context.task_type,
                trust_level=0.5,
                usage_count=10,
                limit=3
            )
            if recommendations:
                skill_text = "\n## 推荐技能\n"
                for rec in recommendations:
                    skill_text += f"- {rec.skill_name}: {rec.reason} (置信度: {rec.confidence:.2f})\n"

        base_prompt = self.config.system_prompt_template.format(
            agent_name=context.agent_id,
            user_id=context.user_id,
            session_id=context.session_id,
            task_type=context.task_type,
            personality_context=personality_text,
            memory_context=memory_text + skill_text,
        )

        # 如果启用 LCM，追加 LCM 协议指令（含内容编码）
        if self.lcm:
            base_prompt = self.lcm.build_system_prompt(base_prompt, user_query=context.task_type)

        return base_prompt

    def _apply_chinese_thinking(self, user_message: str) -> str:
        """Apply Chinese thinking skill to user message."""
        if self._chinese_thinking:
            return self._chinese_thinking.build_thinking_prompt(user_message)
        return user_message

    def _extract_and_format_thinking(self, content: str) -> tuple[str, str]:
        """Extract thinking chain and format output."""
        if self._chinese_thinking and self.config.preserve_thinking_chain:
            thinking, answer = self._chinese_thinking.extract_thinking_chain(content)
            formatted = self._chinese_thinking.format_output(
                thinking_chain=thinking,
                final_answer=answer,
            )
            return formatted, thinking
        return content, ""

    def _build_tools_schema(self) -> list[dict]:
        """Build OpenAI-compatible tool schema from registered tools."""
        tools = []
        for name, func in self._tool_registry.items():
            import inspect
            sig = inspect.signature(func)
            params = {
                "type": "object",
                "properties": {},
                "required": [],
            }
            for param_name, param in sig.parameters.items():
                params["properties"][param_name] = {"type": "string"}
                if param.default is inspect.Parameter.empty:
                    params["required"].append(param_name)

            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": func.__doc__ or f"Tool: {name}",
                    "parameters": params,
                },
            })
        return tools

    async def _execute_tools(self, tool_calls: list[dict]) -> list[ToolCallRecord]:
        """Execute tool calls and return records."""
        records = []
        for tc in tool_calls:
            name = tc.get("function", {}).get("name", "")
            args = tc.get("function", {}).get("arguments", {})
            if isinstance(args, str):
                args = json.loads(args)

            start = datetime.now()
            try:
                func = self._tool_registry.get(name)
                if func:
                    result = await func(**args) if callable(func) else func(**args)
                    records.append(ToolCallRecord(
                        tool_name=name,
                        arguments=args,
                        result=result,
                        latency_ms=int((datetime.now() - start).total_seconds() * 1000),
                        success=True,
                    ))
                else:
                    records.append(ToolCallRecord(
                        tool_name=name,
                        arguments=args,
                        result=f"Tool '{name}' not found",
                        latency_ms=0,
                        success=False,
                    ))
            except Exception as e:
                records.append(ToolCallRecord(
                    tool_name=name,
                    arguments=args,
                    result=str(e),
                    latency_ms=int((datetime.now() - start).total_seconds() * 1000),
                    success=False,
                ))
        return records

    async def run(self, context: ExecutionContext, user_message: str) -> ExecutionResult:
        """Execute the ReAct loop with core technologies."""
        start_time = datetime.now()
        tool_calls: list[ToolCallRecord] = []
        thinking_chain = ""

        try:
            # 1. Load memory
            memory = MemoryContext()
            if self.config.enable_memory:
                memory = await self.memory.load(context.agent_id, context.user_id)

            # 2. Build system prompt
            system_prompt = self._build_system_prompt(context, memory)

            # 3. Apply Chinese thinking skill
            processed_message = self._apply_chinese_thinking(user_message)

            # 4. Build initial messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": processed_message},
            ]

            # 5. ReAct loop
            for step in range(self.config.max_steps):
                tools = self._build_tools_schema() if self._tool_registry else None

                response = await self.provider.chat(
                    messages,
                    tools=tools,
                    tool_choice="auto" if tools else None,
                    temperature=self.config.temperature,
                    max_tokens=self.config.max_tokens_per_step,
                )

                if hasattr(response, 'content') and response.content.startswith("Error:"):
                    return ExecutionResult(
                        content="",
                        error=response.content,
                        steps_taken=step,
                        tool_calls=tool_calls,
                    )

                raw_content = response.content if hasattr(response, 'content') else str(response)

                # 6. LCM: 检测哨兵，加载 chunk
                if self.lcm:
                    clean_text, requests = self.lcm.process_response(raw_content)
                    if requests:
                        req = requests[0]
                        chunk = self.lcm.load_chunk(req.chunk_id)
                        if chunk:
                            messages = self.lcm.inject_chunk(messages, chunk)
                            continue
                        else:
                            return ExecutionResult(
                                content=clean_text,
                                error=f"Chunk '{req.chunk_id}' not found",
                                steps_taken=step,
                                tool_calls=tool_calls,
                            )
                    raw_content = clean_text

                msg = {
                    "role": "assistant",
                    "content": raw_content,
                }
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    msg["tool_calls"] = response.tool_calls
                messages.append(msg)

                # 7. Skill auto-execution based on user message
                if self.config.enable_skills:
                    matched_skills = self.skills.match_skills(
                        user_message,
                        [
                            {
                                "name": s.name,
                                "triggers": self.skills._extract_triggers(s.description, s.name),
                                "instruct": s.prompt_template,
                            }
                            for s in (await self.skills.list_skills())
                        ],
                        max_skills=2
                    )
                    if matched_skills:
                        for matched in matched_skills:
                            skill_result = await self.skills.execute(
                                matched["name"].lower().replace(" ", "_"),
                                params={"text": user_message}
                            )
                            if skill_result.success:
                                messages.append({
                                    "role": "system",
                                    "content": f"[Skill '{matched['name']}'] {skill_result.output}"
                                })

                # 8. Tool calls
                if hasattr(response, 'tool_calls') and response.tool_calls:
                    results = await self._execute_tools(response.tool_calls)
                    for result in results:
                        tool_calls.append(result)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": result.tool_name,
                            "content": str(result.result),
                        })
                    continue

                # 9. Final answer
                formatted_content, extracted_thinking = self._extract_and_format_thinking(raw_content)
                thinking_chain = extracted_thinking

                result = ExecutionResult(
                    content=formatted_content,
                    reasoning=thinking_chain or getattr(response, 'reasoning', ''),
                    steps_taken=step + 1,
                    tool_calls=tool_calls,
                    usage={
                        "prompt_tokens": getattr(getattr(response, 'usage', None), 'prompt_tokens', 0),
                        "completion_tokens": getattr(getattr(response, 'usage', None), 'completion_tokens', 0),
                        "total_tokens": getattr(getattr(response, 'usage', None), 'total_tokens', 0),
                        "latency_ms": getattr(getattr(response, 'usage', None), 'latency_ms', 0),
                    },
                )

                # 10. Save memory
                if self.config.enable_memory:
                    await self.memory.save_message(context.agent_id, {"role": "user", "content": user_message})
                    await self.memory.save_message(context.agent_id, {"role": "assistant", "content": result.content})

                # 11. Skill distillation
                if self.config.enable_skill_distillation and tool_calls:
                    skill = await self.skills.distill(
                        task_description=user_message,
                        conversation=messages,
                        success=True,
                    )
                    if skill:
                        result.skills_distilled.append(skill.id)

                return result

            return ExecutionResult(
                content="",
                error="Max steps reached without final answer",
                steps_taken=self.config.max_steps,
                tool_calls=tool_calls,
            )

        except Exception as e:
            return ExecutionResult(
                content="",
                error=str(e),
                steps_taken=0,
                tool_calls=tool_calls,
            )
