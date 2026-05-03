"""
API 端点集成测试 �?使用 httpx 客户端测�?FastAPI
"""
import sys
import os
import pytest
from httpx import ASGITransport, AsyncClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 必须在导�?server 前设置环�?os.environ["OPENAI_API_KEY"] = "sk-test-key"
os.environ["OPENAI_BASE_URL"] = "https://api.test.com/v1"
os.environ["OPENAI_MODEL"] = "test-model"

from server.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_root_endpoint(client):
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert "version" in data
    assert "modules" in data


@pytest.mark.asyncio
async def test_list_agents(client):
    resp = await client.get("/agents")
    assert resp.status_code == 200
    data = resp.json()
    assert "agents" in data
    assert len(data["agents"]) >= 3  # iris, codey, scribe


@pytest.mark.asyncio
async def test_get_agent_iris(client):
    resp = await client.get("/agents/iris")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "iris"
    assert data["name"] == "爱弥�?


@pytest.mark.asyncio
async def test_get_agent_not_found(client):
    resp = await client.get("/agents/nonexistent_agent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_delete_agent(client):
    # Create
    create_resp = await client.post(
        "/agents/create",
        json={
            "name": "测试�?,
            "title": "测试助手",
            "specialty": "自动化测�?,
            "emoji": "🧪",
        },
    )
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["agent"]["name"] == "测试�?

    # Get created agent
    agent_id = created["agent"]["id"]
    get_resp = await client.get(f"/agents/{agent_id}")
    assert get_resp.status_code == 200

    # Update
    update_resp = await client.put(
        f"/agents/{agent_id}",
        json={"specialty": "全栈测试"},
    )
    assert update_resp.status_code == 200

    # Delete
    delete_resp = await client.delete(f"/agents/{agent_id}")
    assert delete_resp.status_code == 200


@pytest.mark.asyncio
async def test_cannot_delete_iris(client):
    resp = await client.delete("/agents/iris")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_settings(client):
    resp = await client.get("/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert "providers" in data


@pytest.mark.asyncio
async def test_memrag_status(client):
    resp = await client.get("/memrag")
    assert resp.status_code == 200
    data = resp.json()
    assert "enabled" in data


if __name__ == "__main__":
    pytest.main(["-v", "-x", __file__])
