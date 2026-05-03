"""
MCP Client �?Model Context Protocol 客户�?
连接本地 MCP 服务器并暴露其工具给 Agent�?
轻量实现：通过 stdio 子进程与 MCP 服务器通信�?
"""

import json
import subprocess
import asyncio
from typing import Optional
from agent_core.settings.settings_store import MCPConfig


class MCPServerClient:
    """单个 MCP 服务器连�?""

    def __init__(self, config: MCPConfig):
        self.config = config
        self._process: subprocess.Popen | None = None
        self._tools: list[dict] = []
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def tools(self) -> list[dict]:
        return self._tools

    def connect(self) -> bool:
        """启动 MCP 服务器进程并初始�?""
        if self._connected:
            return True
        try:
            self._process = subprocess.Popen(
                [self.config.command, *self.config.args],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={**__import__('os').environ, **self.config.env},
            )
            # 发�?initialize 请求
            self._send_request("initialize", {
                "protocolVersion": "0.1.0",
                "capabilities": {},
                "clientInfo": {"name": "iris-agent", "version": "0.1.0"},
            })
            # 获取工具列表
            tools_resp = self._send_request("tools/list", {})
            self._tools = tools_resp.get("tools", [])
            self._connected = True
            return True
        except Exception as e:
            print(f"[MCP] Failed to connect {self.config.name}: {e}")
            return False

    def call_tool(self, tool_name: str, arguments: dict) -> str:
        """调用 MCP 工具"""
        if not self._connected:
            return f"[MCP Error] Server {self.config.name} not connected"
        try:
            resp = self._send_request("tools/call", {
                "name": tool_name,
                "arguments": arguments,
            })
            content = resp.get("content", [])
            # 提取文本内容
            texts = [c.get("text", "") for c in content if c.get("type") == "text"]
            return "\n".join(texts) if texts else json.dumps(resp, ensure_ascii=False)
        except Exception as e:
            return f"[MCP Error] {e}"

    def disconnect(self):
        """断开连接"""
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._connected = False
        self._tools = []
        self._process = None

    def _send_request(self, method: str, params: dict) -> dict:
        """发�?JSON-RPC 请求"""
        if not self._process or not self._process.stdin:
            raise ConnectionError("Process not started")

        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params,
        }
        line = json.dumps(request, ensure_ascii=False) + "\n"
        self._process.stdin.write(line)
        self._process.stdin.flush()

        # 读取响应
        response_line = self._process.stdout.readline()
        if not response_line:
            raise ConnectionError("No response from MCP server")
        response = json.loads(response_line)
        if "error" in response:
            raise RuntimeError(response["error"].get("message", str(response["error"])))
        return response.get("result", {})

    def __del__(self):
        self.disconnect()


class MCPManager:
    """MCP 管理�?�?管理多个 MCP 服务�?""

    def __init__(self):
        self._servers: dict[str, MCPServerClient] = {}

    def load_configs(self, configs: list[MCPConfig]):
        """从配置列表加�?MCP 服务�?""
        # 关闭已移除的
        old_ids = set(self._servers.keys())
        new_ids = {c.id for c in configs if c.enabled}
        for oid in old_ids - new_ids:
            self._servers[oid].disconnect()
            del self._servers[oid]

        # 启动新的
        for config in configs:
            if config.enabled and config.id not in self._servers:
                client = MCPServerClient(config)
                if client.connect():
                    self._servers[config.id] = client

    def get_all_tools(self) -> list[dict]:
        """获取所有已连接 MCP 服务器的工具"""
        tools = []
        for sid, server in self._servers.items():
            for tool in server.tools:
                tool["_mcp_server_id"] = sid
                tools.append(tool)
        return tools

    def call_tool(self, server_id: str, tool_name: str, arguments: dict) -> str:
        """在指定服务器上调用工�?""
        server = self._servers.get(server_id)
        if not server:
            return f"[MCP Error] Server '{server_id}' not found"
        return server.call_tool(tool_name, arguments)

    def disconnect_all(self):
        """断开所�?MCP 连接"""
        for server in self._servers.values():
            server.disconnect()
        self._servers.clear()


# 全局单例
mcp_manager = MCPManager()
