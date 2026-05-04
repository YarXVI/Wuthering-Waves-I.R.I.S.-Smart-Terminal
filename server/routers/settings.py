"""
Router: Settings Management (API Providers, MCP, Skills)
"""
from fastapi import APIRouter
from agent_core.settings.settings_store import settings_store
from agent_core.providers import registry
from agent_core.mcp.mcp_client import mcp_manager
from agent_core.skills_registry import skills_registry
from agent_core.core.agent_manager import manager

router = APIRouter()


@router.get("/settings")
def get_settings():
    """Get all settings (API Key automatically masked)"""
    return settings_store.to_dict_masked()


@router.get("/settings/providers")
def list_providers():
    """List all API providers"""
    providers = registry.providers
    return {"providers": list(providers.values())}


@router.post("/settings/providers")
def update_providers(req: dict):
    """Update API providers list"""
    providers_data = req.get("providers", [])
    settings_store.update_providers(providers_data)
    from agent_core.settings.settings_store import ProviderConfig
    configs = [ProviderConfig(**p) for p in providers_data]
    registry.reload_all(configs)
    return {"status": "ok"}


@router.get("/settings/mcp")
def list_mcp_servers():
    """List MCP server status"""
    servers = []
    configured = settings_store.settings.mcp_servers if hasattr(settings_store, 'settings') else []

    if hasattr(mcp_manager, '_servers') and mcp_manager._servers:
        for sid, server in mcp_manager._servers.items():
            servers.append({
                "id": sid,
                "name": server.config.name if hasattr(server, 'config') else sid,
                "connected": server.is_connected if hasattr(server, 'is_connected') else False,
                "tools": len(server.tools) if hasattr(server, 'tools') else 0,
            })
    else:
        for cfg in configured:
            servers.append({
                "id": cfg.get("id", "unknown"),
                "name": cfg.get("name", "Unknown Server"),
                "connected": False,
                "tools": 0,
            })

    return {"servers": servers, "configured": len(configured)}


@router.post("/settings/mcp")
def update_mcp_servers(req: dict):
    """Update MCP server configuration"""
    servers_data = req.get("servers", [])
    settings_store.update_mcp_servers(servers_data)
    from agent_core.settings.settings_store import MCPConfig
    configs = [MCPConfig(**s) for s in servers_data]
    mcp_manager.load_configs(configs)
    return {"status": "ok"}
