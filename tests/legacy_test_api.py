"""Integration test for agents HTTP API"""
import subprocess, time, json, urllib.request, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# Clean up any leftover test data
from agent_core.core.agent_store import load_agents, save_agents
agents = load_agents()
agents.pop("剪辑?, None)
save_agents(agents)
# Start server
proc = subprocess.Popen(
[sys.executable, 'server/main.py'],
stdout=subprocess.PIPE, stderr=subprocess.PIPE
)
time.sleep(5)
base_url = 'http://127.0.0.1:8765'
try:
# Test list agents
resp = urllib.request.urlopen(f'{base_url}/agents')
data = json.loads(resp.read())
print(f'GET /agents: {len(data["agents"])} agents')
for a in data['agents']:
print(f'  {a["id"]}: {a["name"]} [{a["specialty"][:25]}]')
# Test create
body = json.dumps({
'name': '剪辑?,
'title': '视频剪辑?,
'specialty': '视频脚本、分镜、剪?,
'emoji': '🎬'
}).encode()
req = urllib.request.Request(
f'{base_url}/agents/create',
data=body,
headers={'Content-Type': 'application/json'}
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
print(f'\nPOST /agents/create: {data["agent"]["name"]} (id={data["agent"]["id"]})')
# Test list again (should be 4)
resp = urllib.request.urlopen(f'{base_url}/agents')
data = json.loads(resp.read())
print(f'GET /agents: {len(data["agents"])} agents')
# Test get single
resp = urllib.request.urlopen(f'{base_url}/agents/%E5%89%AA%E8%BE%91%E5%B8%88')
data = json.loads(resp.read())
print(f'GET /agents/剪辑? {data["name"]} [{data["specialty"]}]')
# Test update
body = json.dumps({'specialty': '视频脚本、分镜设计、内容策划、剪辑特?}).encode()
req = urllib.request.Request(
f'{base_url}/agents/%E5%89%AA%E8%BE%91%E5%B8%88',
data=body,
headers={'Content-Type': 'application/json'},
method='PUT'
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
print(f'PUT /agents/剪辑? {data["message"]}')
# Test delete
req = urllib.request.Request(
f'{base_url}/agents/%E5%89%AA%E8%BE%91%E5%B8%88',
method='DELETE'
)
resp = urllib.request.urlopen(req)
data = json.loads(resp.read())
print(f'DELETE /agents/剪辑? {data["message"]}')
# Verify deletion (should be 3 again)
resp = urllib.request.urlopen(f'{base_url}/agents')
data = json.loads(resp.read())
print(f'After delete - GET /agents: {len(data["agents"])} agents')
# Test 404
try:
urllib.request.urlopen(f'{base_url}/agents/nonexistent')
print('ERROR: should have raised 404')
except urllib.error.HTTPError as e:
print(f'GET /agents/nonexistent: 404 OK (code={e.code})')
# Test 403 - cannot delete iris
try:
req = urllib.request.Request(f'{base_url}/agents/iris', method='DELETE')
urllib.request.urlopen(req)
print('ERROR: should have raised 403')
except urllib.error.HTTPError as e:
print(f'DELETE /agents/iris: 403 OK (code={e.code})')
print('\n=== ALL HTTP TESTS PASSED ===')
finally:
proc.terminate()
proc.wait()
time.sleep(1)