"""
Agent Collaboration Tools - Enable agents to call each other
Each agent gets a call_agent tool to send messages and get responses from other agents
"""

from agent_core.utils.isolation import safe_call


CALL_AGENT_TOOL = {
    "type": "function",
    "function": {
        "name": "call_agent",
        "description": "Send a message to a specified colleague (Agent) and get their professional response. Only use when user explicitly mentions a colleague.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Target colleague ID",
                },
                "message": {
                    "type": "string",
                    "description": "Message content to send to colleague",
                },
                "provide_context": {
                    "type": "boolean",
                    "description": "Whether to automatically include current conversation context",
                },
            },
            "required": ["agent_id", "message"],
        },
    },
}


def call_agent_handler(agent_id: str, message: str, provide_context: bool = False) -> dict:
    """Handle call_agent tool invocation"""
    from agent_core.core.agent_manager import manager

    agent = manager.get_agent(agent_id)
    if not agent:
        return {"success": False, "error": f"Agent {agent_id} not found"}

    response = agent.chat(message)
    return {"success": True, "response": response}


def get_agent_collaboration_tools() -> list:
    """Get all collaboration tools"""
    return [CALL_AGENT_TOOL]


def get_agent_collaboration_handlers() -> dict:
    """Get all collaboration tool handlers"""
    return {
        "call_agent": call_agent_handler,
    }
