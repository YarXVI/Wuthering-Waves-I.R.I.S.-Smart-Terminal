"""
Agent Runtime - Core brain
All external dependencies (MCP, skills) are loaded through isolation layer
"""

from agent_core.core.llm import LLMClient
from agent_core.tools.file_search import (
    search_local_files,
    read_file_content,
    FILE_SEARCH_TOOL,
    FILE_READER_TOOL,
)
from agent_core.memory.session_store import save_session, load_session, delete_session, archive_session
from agent_core.utils.isolation import safe_call, safe_import
from agent_core.utils.text import strip_emoji

# ---- Isolated loading: MCP Manager (works whether available or not) ----
_mcp_mod = safe_import("agent_core.mcp.mcp_client")
_mcp_manager = getattr(_mcp_mod, "mcp_manager", None) if _mcp_mod else None

# ---- Isolated loading: Skills registry + injector ----
_skills_mod = safe_import("agent_core.skills_registry")
_skills_registry = getattr(_skills_mod, "skills_registry", None) if _skills_mod else None
_injector_mod = safe_import("agent_core.skills_registry.injector")
_skill_injector = getattr(_injector_mod, "injector", None) if _injector_mod else None

# ---- Isolated loading: Agent collaboration tools ----
_collab_mod = safe_import("agent_core.collaboration.agent_tools")
_collab_get_tools = getattr(_collab_mod, "get_agent_collaboration_tools", None) if _collab_mod else None
_collab_get_handlers = getattr(_collab_mod, "get_agent_collaboration_handlers", None) if _collab_mod else None


class Agent:
    """Agent runtime - manages conversation and tool execution"""

    def __init__(
        self,
        name: str,
        model: str = "gpt-4o",
        api_key: str = None,
        system_prompt: str = "",
    ):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.llm = LLMClient(model=model, api_key=api_key)

    def chat(self, message: str, history: list = None) -> str:
        """Send a chat message and get response"""
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        response = self.llm.chat(messages)
        return response

    def get_tools(self) -> list:
        """Get available tools for this agent"""
        tools = [
            FILE_SEARCH_TOOL,
            FILE_READER_TOOL,
        ]

        # Add MCP tools if available
        if _mcp_manager:
            mcp_tools = safe_call(getattr, [], _mcp_manager, "get_tools")
            if mcp_tools:
                tools.extend(mcp_tools)

        # Add collaboration tools if available
        if _collab_get_tools:
            collab_tools = safe_call(_collab_get_tools, [])
            if collab_tools:
                tools.extend(collab_tools)

        return tools

    def save_state(self, session_id: str) -> bool:
        """Save agent state to session"""
        try:
            state = {
                "name": self.name,
                "model": self.model,
                "system_prompt": self.system_prompt,
            }
            return save_session(session_id, state)
        except:
            return False

    def load_state(self, session_id: str) -> bool:
        """Load agent state from session"""
        try:
            state = load_session(session_id)
            if state:
                self.name = state.get("name", self.name)
                self.model = state.get("model", self.model)
                self.system_prompt = state.get("system_prompt", self.system_prompt)
                return True
            return False
        except:
            return False
