"""
Collaboration - Multi-Agent collaboration system
Supports Agent-to-Agent invocation, task orchestration, result aggregation
"""
from agent_core.collaboration.agent_tools import (
    CALL_AGENT_TOOL,
    call_agent_handler,
    get_agent_collaboration_tools,
)
from agent_core.collaboration.orchestrator import (
    Orchestrator,
)

orchestrator = Orchestrator()
