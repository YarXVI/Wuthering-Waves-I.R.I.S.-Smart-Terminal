"""

AIAgent 核心引擎 - 重构后的增强版 Agent

支持可中断API调用、并发工具执行、消息角色校验、迭代预算跟踪

"""



import json

import threading

from concurrent.futures import ThreadPoolExecutor, as_completed

from dataclasses import dataclass, field

from typing import Any



from agent_core.core.llm import LLMClient

from agent_core.core.api_adapter import APIAdapterFactory, APIModeRouter, create_default_router

from agent_core.core.compression import (

    CompressionEngine,

    RoleValidator,

    IterationBudget,

    InterruptibleCall,

    CriticalInfo,

    MessageState,

)

from agent_core.core.callback import (

    CallbackManager,

    Event,

    EventType,

    InterruptibleContext,

    StateTracker,

    create_default_callback_manager,

)

from agent_core.core.prompt_builder import PromptBuilder, SkillInjector

from agent_core.tools.file_search import (

    search_local_files,

    read_file_content,

    FILE_SEARCH_TOOL,

    FILE_READER_TOOL,

)

from agent_core.memory.session_store import save_session, load_session, delete_session, archive_session

from agent_core.utils.isolation import safe_call, safe_import

from agent_core.utils.text import strip_emoji





_mcp_mod = safe_import("agent_core.mcp.mcp_client")

_mcp_manager = getattr(_mcp_mod, "mcp_manager", None) if _mcp_mod else None



_skills_mod = safe_import("agent_core.skills_registry")

_skills_registry = getattr(_skills_mod, "skills_registry", None) if _skills_mod else None

_injector_mod = safe_import("agent_core.skills_registry.injector")

_skill_injector = getattr(_injector_mod, "injector", None) if _injector_mod else None



_collab_mod = safe_import("agent_core.collaboration.agent_tools")

_collab_get_tools = getattr(_collab_mod, "get_agent_collaboration_tools", None) if _collab_mod else None

_collab_get_handlers = getattr(_collab_mod, "get_agent_collaboration_handlers", None) if _collab_mod else None





DEFAULT_SYSTEM_PROMPT = """你是一个智能工作助手，名叫 I.R.I.S.

## 你的角色

你是一个驻AI助手，像办公室员工一样工作。



## 可用工具

- search_local_files：在本地文件中搜索关键词，查找笔记和文档

- read_file_content：读取指定文件的完整内容



## 工作方式

1. 接到任务后，先理解用户真正想要什么

2. 如果信息不够，主动追问

3. 如果需要查阅资料，使用工具搜索和读取本地文件

4. 整理信息后，给出清晰、结构化的回答



## 输出要求

- 结构化：使用标题、列表、代码块等组织内容

- 有价值：给出见解和建议，不只是罗列信息

- 诚实：找不到就说找不到，不编造信息

"""





@dataclass

class AIAgentConfig:

    """AIAgent 配置"""

    max_iterations: int = 10

    max_tool_concurrency: int = 3

    enable_compression: bool = True

    compression_threshold: int = 4000

    enable_role_validation: bool = True

    api_mode: str = "chat_completions"

    temperature: float = 0.3





class AIAgent:

    """增强版 Agent 运行引擎"""



    def __init__(

        self,

        agent_id: str = "",

        system_prompt_override: str | None = None,

        provider_id: str | None = None,

        config: AIAgentConfig | None = None,

    ):

        self.agent_id = agent_id

        self.provider_id = provider_id

        self.config = config or AIAgentConfig()



        self.llm = LLMClient(provider_id=provider_id)

        self.system_prompt = system_prompt_override or DEFAULT_SYSTEM_PROMPT

        self.messages: list[dict] = []



        self.tools = [FILE_SEARCH_TOOL, FILE_READER_TOOL]

        self.tool_handlers: dict[str, callable] = {

            "search_local_files": search_local_files,

            "read_file_content": read_file_content,

        }



        self._mcp_available = _mcp_manager is not None

        self._skills_available = _skills_registry is not None

        self._collab_available = _collab_get_tools is not None and _collab_get_handlers is not None



        self._role_validator = RoleValidator()

        self._iteration_budget = IterationBudget(max_iterations=self.config.max_iterations)

        self._compression_engine = CompressionEngine(max_tokens=self.config.compression_threshold)

        self._compression_engine.set_llm_client(self.llm)



        self._callback_manager = create_default_callback_manager()

        self._interrupt_ctx = InterruptibleContext()

        self._state_tracker = StateTracker()



        self._prompt_builder = PromptBuilder(base_prompt=self.system_prompt)

        self._skill_injector_obj = SkillInjector(skill_registry=_skills_registry)



        self._api_mode_router = create_default_router()



        self._thread_pool: ThreadPoolExecutor | None = None

        if self.config.max_tool_concurrency > 1:

            self._thread_pool = ThreadPoolExecutor(

                max_workers=self.config.max_tool_concurrency

            )



        self._try_load()

        self._trigger_event(EventType.ON_START, {"agent_id": agent_id})



    def _try_load(self):

        """尝试从磁盘加载之前的对话历史"""

        if not self.agent_id:

            self.messages = [{"role": "system", "content": self.system_prompt}]

            return

        session = safe_call(load_session, None, self.agent_id)

        if session is None:

            self.messages = [{"role": "system", "content": self.system_prompt}]

            return

        self.messages = [

            {"role": "system", "content": self.system_prompt},

            *session.get("messages", []),

        ]



    def _trigger_event(self, event_type: EventType, data: dict | None = None):

        """触发回调事件"""

        event = Event(event_type=event_type, data=data or {})

        self._callback_manager.trigger(event)



    def _build_runtime_tools(self) -> list[dict]:

        """构建运行时工具列表"""

        all_tools = list(self.tools)



        if self._mcp_available:

            mcp_tools = safe_call(_mcp_manager.get_all_tools, [])

            for t in mcp_tools:

                prefixed = dict(t)

                prefixed["name"] = f"mcp_{t['name']}"

                all_tools.append(prefixed)



        if self._collab_available:

            collab_tools = safe_call(_collab_get_tools, [])

            all_tools.extend(collab_tools)



        return all_tools



    def _execute_tool_call(

        self,

        fn_name: str,

        fn_args: dict,

    ) -> tuple[str, str, str]:

        """执行单个工具调用，返回 (call_id, fn_name, result)"""

        result = self._handle_runtime_tool_call(fn_name, fn_args)

        return ("", fn_name, result)



    def _execute_concurrent_tools(

        self,

        tool_calls: list[dict],

    ) -> list[tuple[str, str, str]]:

        """并发执行多个工具调用"""

        if not self._thread_pool or len(tool_calls) <= 1:

            results = []

            for tc in tool_calls:

                call_id, fn_name, fn_args_str = self._extract_tool_call_info(tc)

                try:

                    fn_args = json.loads(fn_args_str)

                except (json.JSONDecodeError, Exception):

                    fn_args = {}

                result = self._handle_runtime_tool_call(fn_name, fn_args)

                results.append((call_id, fn_name, result))

            return results



        futures = []

        for tc in tool_calls:

            call_id, fn_name, fn_args_str = self._extract_tool_call_info(tc)

            try:

                fn_args = json.loads(fn_args_str)

            except (json.JSONDecodeError, Exception):

                fn_args = {}



            future = self._thread_pool.submit(

                self._handle_runtime_tool_call,

                fn_name,

                fn_args,

            )

            futures.append((call_id, fn_name, future))



        results = []

        for call_id, fn_name, future in futures:

            try:

                result = future.result(timeout=30)

            except Exception as e:

                result = f"[Tool Error] {str(e)[:200]}"

            results.append((call_id, fn_name, result))



        return results



    def interrupt(self):

        """请求中断当前执行"""

        self._interrupt_ctx.interrupt()

        self._trigger_event(EventType.ON_INTERRUPT_REQUESTED, {})



    def _check_interruption(self):

        """检查是否被中断"""

        if self._interrupt_ctx.is_interrupted():

            return True

        return False



    def _validate_role_sequence(self) -> tuple[bool, str]:

        """验证消息角色序列"""

        if not self.config.enable_role_validation:

            return True, ""



        self._role_validator.reset()

        for msg in self.messages:

            role = msg.get("role", "")

            if role == "tool":

                role = "tool"

            self._role_validator.add_message(role)



        return self._role_validator.validate_history()



    def _compress_if_needed(self):

        """必要时压缩上下文"""

        if not self.config.enable_compression:

            return



        total_tokens = sum(

            len(m.get("content", "")) // 2

            for m in self.messages

        )



        if total_tokens > self.config.compression_threshold * 1.5:

            critical_info = self._extract_critical_info()

            compressed, preserved = self._compression_engine.compress(

                self.messages,

                critical_info,

            )

            if len(compressed) < len(self.messages):

                self.messages = compressed

                self._trigger_event(EventType.ON_COMPRESSION, {

                    "original_count": len(self.messages),

                    "compressed_count": len(compressed),

                    "preserved_count": len(preserved),

                })



    def _extract_critical_info(self) -> list[CriticalInfo]:

        """提取关键信息"""

        critical = []



        if self.messages and self.messages[0].get("role") == "system":

            critical.append(CriticalInfo(

                key="system_identity",

                value="I.R.I.S. 智能助手",

                priority=10,

            ))



        critical.append(CriticalInfo(

            key="agent_capabilities",

            value="可用工具: search_local_files, read_file_content",

            priority=5,

        ))



        return critical



    def _handle_runtime_tool_call(self, fn_name: str, fn_args: dict) -> str:

        """处理工具调用"""

        handler = self.tool_handlers.get(fn_name)

        if handler:

            return safe_call(handler, f"[Tool Error] {fn_name} failed", **fn_args)



        if fn_name.startswith("mcp_") and self._mcp_available:

            real_name = fn_name[4:]

            servers = safe_call(lambda: getattr(_mcp_manager, '_servers', {}), {})

            for sid, server in servers.items():

                for tool in server.tools:

                    if tool["name"] == real_name:

                        return safe_call(

                            server.call_tool,

                            f"[MCP Failed] {real_name}",

                            real_name,

                            fn_args,

                        )

            return f"[MCP] Tool '{real_name}' not found"



        if self._collab_available:

            handlers = safe_call(_collab_get_handlers, {})

            collab_handler = handlers.get(fn_name)

            if collab_handler:

                return safe_call(

                    collab_handler,

                    f"[Collaboration Error] {fn_name} failed",

                    **fn_args,

                )



        return f"[Unknown Tool] '{fn_name}'"



    def _extract_content_from_message(self, message) -> tuple[str, str, list | None]:

        """提取消息内容"""

        if isinstance(message, dict):

            content = message.get("content", "")

            reasoning = message.get("reasoning", "")

            tool_calls = message.get("tool_calls")

        else:

            content = getattr(message, "content", "")

            reasoning = getattr(message, "reasoning_content", "")

            tool_calls = getattr(message, "tool_calls", None)

        return content, reasoning, tool_calls



    def _extract_tool_call_info(self, tc) -> tuple[str, str, str]:

        """提取工具调用信息"""

        if isinstance(tc, dict):

            call_id = tc["id"]

            fn_name = tc["function"]["name"]

            fn_args_str = tc["function"]["arguments"]

        else:

            call_id = tc.id

            fn_name = tc.function.name

            fn_args_str = tc.function.arguments

        return call_id, fn_name, fn_args_str



    def run(self, user_input: str) -> str:

        """处理用户输入"""

        self._interrupt_ctx.reset()

        self._iteration_budget.current_iteration = 0

        self._iteration_budget.reset_tool_calls()



        self.messages.append({"role": "user", "content": user_input})



        if not self.messages or self.messages[0]["role"] != "system":

            self.messages.insert(0, {"role": "system", "content": self.system_prompt})



        if self._skills_available and _skill_injector:

            enriched = safe_call(

                _skill_injector.inject,

                self.system_prompt,

                user_input,

                self.system_prompt,

            )

            if enriched:

                self.messages[0]["content"] = enriched



        all_tools = self._build_runtime_tools()



        while self._iteration_budget.has_budget():

            self._iteration_budget.next_iteration()

            self._trigger_event(EventType.ON_ITERATION_START, {

                "iteration": self._iteration_budget.current_iteration,

            })



            if self._check_interruption():

                return "[Interrupted] 执行被中断"



            self._trigger_event(EventType.ON_API_CALL_START, {

                "iteration": self._iteration_budget.current_iteration,

            })



            try:

                api_mode = self._api_mode_router.route(

                    self.messages,

                    {"provider": self.provider_id},

                )

                message = self.llm.chat(

                    self.messages,

                    tools=all_tools if all_tools else None,

                    temperature=self.config.temperature,

                )

            except Exception as e:

                self._trigger_event(EventType.ON_API_ERROR, {"error": str(e)})

                error_msg = f"[API Error] {str(e)[:200]}"

                self.messages.append({"role": "assistant", "content": error_msg})

                self.save()

                return error_msg

            finally:

                self._trigger_event(EventType.ON_API_CALL_END, {})



            content, reasoning, tool_calls = self._extract_content_from_message(message)



            if not tool_calls:

                final_content = content or reasoning or ""

                final_content = strip_emoji(final_content)

                self.messages.append({"role": "assistant", "content": final_content})

                self.save()

                self._trigger_event(EventType.ON_ITERATION_END, {

                    "iteration": self._iteration_budget.current_iteration,

                    "final": True,

                })

                return final_content



            msg_dict: dict[str, Any] = {"role": "assistant", "content": content or ""}

            if tool_calls:

                msg_dict["tool_calls"] = tool_calls

            self.messages.append(msg_dict)



            self._iteration_budget.reset_tool_calls()

            tool_results = self._execute_concurrent_tools(tool_calls)



            for call_id, fn_name, result in tool_results:

                self._iteration_budget.record_tool_call()

                self._trigger_event(EventType.ON_TOOL_CALL_END, {

                    "tool": fn_name,

                    "call_id": call_id,

                })



                tool_msg = {

                    "role": "tool",

                    "tool_call_id": call_id or None,

                    "content": str(result),

                }

                self.messages.append(tool_msg)



                if self.config.enable_role_validation:

                    self._role_validator.add_message("assistant")

                    self._role_validator.add_message("tool")



            if self.config.enable_role_validation:

                is_valid, error = self._validate_role_sequence()

                if not is_valid:

                    print(f"[RoleValidation] Warning: {error}")



            self._compress_if_needed()



            self._trigger_event(EventType.ON_ITERATION_END, {

                "iteration": self._iteration_budget.current_iteration,

                "final": False,

            })



        self._trigger_event(EventType.ON_MAX_ITERATIONS_REACHED, {

            "total_iterations": self._iteration_budget.current_iteration,

        })



        self.messages.append({

            "role": "user",

            "content": "请基于已有信息尽快给出最终回答。",

        })



        try:

            reply_result = self.llm.chat(self.messages)

            reply, _, _ = self._extract_content_from_message(reply_result)

        except Exception as e:

            reply = f"[API Error] {str(e)[:200]}"



        reply = strip_emoji(reply or "")

        self.messages.append({"role": "assistant", "content": reply})

        self.save()

        return reply



    def set_temporary_prompt(self, enriched_prompt: str) -> str:

        """临时替换系统提示词"""

        old_prompt = self.system_prompt

        self.system_prompt = enriched_prompt

        if self.messages and self.messages[0]["role"] == "system":

            self.messages[0]["content"] = enriched_prompt

        return old_prompt



    def save(self):

        """持久化当前对话"""

        if not self.agent_id:

            return

        safe_call(save_session, None, self.agent_id, self.messages)



    def reset(self):

        """重置对话上下文"""

        self.messages = [{"role": "system", "content": self.system_prompt}]

        if self.agent_id:

            safe_call(delete_session, None, self.agent_id)

        self._role_validator.reset()

        self._iteration_budget.current_iteration = 0

        self._iteration_budget.reset_tool_calls()

        self._interrupt_ctx.reset()



    def new_session(self) -> str | None:

        """新建会话"""

        archive_name = safe_call(archive_session, None, self.agent_id)

        self.reset()

        return archive_name



    @property

    def message_count(self) -> int:

        chat_msgs = [m for m in self.messages if m["role"] != "system"]

        return len(chat_msgs) // 2



    def register_callback(self, handler):

        """注册回调处理器"""

        self._callback_manager.register_global(handler)



    def get_state(self) -> dict:

        """获取当前状态"""

        return {

            "agent_id": self.agent_id,

            "message_count": self.message_count,

            "iteration_status": self._iteration_budget.get_status(),

            "is_interrupted": self._interrupt_ctx.is_interrupted(),

            "role_sequence": self._role_validator.get_sequence_type(),

        }



    def shutdown(self):

        """关闭 Agent，释放资源"""

        if self._thread_pool:

            self._thread_pool.shutdown(wait=False)

        self._trigger_event(EventType.ON_END, {})





class Agent(AIAgent):

    """兼容性别名 - 原有 Agent 类指向 AIAgent"""



    def __init__(self, agent_id: str = "", system_prompt_override: str | None = None,

                 provider_id: str | None = None):

        super().__init__(agent_id, system_prompt_override, provider_id)

