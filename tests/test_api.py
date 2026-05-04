"""



"""
API 绔偣闆嗘垚娴嬭瘯 鈥?浣跨敤 httpx 瀹㈡埛绔祴璇?FastAPI





"""



"""
import sys





import os





import pytest





from httpx import ASGITransport, AsyncClient





sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))





# 蹇呴』鍦ㄥ鍏?server 鍓嶈缃幆澧?os.environ["OPENAI_API_KEY"] = "sk-test-key"





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





assert data["name"] == "鐖卞讥鏂?





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





"name": "娴嬭瘯鍛?,





"title": "娴嬭瘯鍔╂墜",





"specialty": "鑷姩鍖栨祴璇?,





"emoji": "馃И",





},





)





assert create_resp.status_code == 200





created = create_resp.json()





assert created["agent"]["name"] == "娴嬭瘯鍛?





# Get created agent





agent_id = created["agent"]["id"]





get_resp = await client.get(f"/agents/{agent_id}")





assert get_resp.status_code == 200





# Update





update_resp = await client.put(





f"/agents/{agent_id}",





json={"specialty": "鍏ㄦ爤娴嬭瘯"},





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




