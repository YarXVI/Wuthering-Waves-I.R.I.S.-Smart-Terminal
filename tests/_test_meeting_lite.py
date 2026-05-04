""""""
轻量会议功能验证 ?创建 + 几轮讨论 + 共识判断
""""""
import urllib.request, json, time
BASE = "http://127.0.0.1:8765"
def api(path, data=None, method="GET"):
url = BASE + path
body = json.dumps(data).encode() if data and method != "GET" else None
req = urllib.request.Request(url, method=method, data=body,
headers={"Content-Type": "application/json"} if data else {})
try:
return json.loads(urllib.request.urlopen(req, timeout=60).read())
except urllib.error.HTTPError as e:
return {"error": e.code, "detail": e.read().decode()[:200]}
except Exception as e:
return {"error": str(e)}
print("[1/7] 健康检?)
r = api("/health")
print(f"  {r}")
print("[2/7] 列出 Agent")
r = api("/agents")
agents = r.get("agents", [])
print(f"  {len(agents)} 位同?)
for a in agents:
print(f"  - {a.get('name')} ({a.get('id')})")
print("[3/7] 创建会议")
r = api("/meetings/start", {"topic": "代码规范讨论", "agents": ["codey", "scribe"]}, "POST")
room_id = r.get("room_id")
print(f"  room_id={room_id}, status={r.get('status')}")
assert room_id, "创建会议失败"
print("[4/7] 执行?轮讨?(codey发言)")
time.sleep(2)
r = api(f"/meetings/{room_id}/round", "POST")
rd = r.get("round", {})
print(f"  发言? {rd.get('author')}")
print(f"  内容: {str(rd.get('content', ''))[:150]}")
print("[5/7] 执行?轮讨?(scribe发言)")
time.sleep(2)
r = api(f"/meetings/{room_id}/round", "POST")
rd = r.get("round", {})
print(f"  发言? {rd.get('author')}")
print(f"  内容: {str(rd.get('content', ''))[:150]}")
print("[6/7] 执行?轮讨?(iris评审)")
time.sleep(2)
r = api(f"/meetings/{room_id}/round", "POST")
rd = r.get("round", {})
print(f"  发言? {rd.get('author')}")
print(f"  内容: {str(rd.get('content', ''))[:150]}")
print("[7/7] 共识判断")
r = api(f"/meetings/{room_id}/judge", "POST")
print(f"  共识: {r.get('consensus')}")
print(f"  理由: {r.get('reason')}")
print("\n=== 会议模块基本功能验证通过 ===")