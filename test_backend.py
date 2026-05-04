
import requests
import json

print("=== Testing Backend API Endpoints ===")
print("=" * 50)

# Test health endpoint
print("\n1. Testing /health")
try:
    r = requests.get('http://localhost:8000/health')
    print(f"   Status: {r.status_code}")
    print("   Response:", json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"   Error: {e}")

# Test agents endpoint
print("\n2. Testing /agents")
try:
    r = requests.get('http://localhost:8000/agents')
    print(f"   Status: {r.status_code}")
    data = r.json()
    print(f"   Agents count: {len(data.get('agents', []))}")
    for agent in data.get('agents', [])[:3]:  # Show first 3
        print(f"   - {agent.get('name')} ({agent.get('id')})")
except Exception as e:
    print(f"   Error: {e}")

# Test chat endpoint
print("\n3. Testing /chat")
try:
    r = requests.post('http://localhost:8000/chat', json={'message': 'Hello!', 'agent_id': 'iris'})
    print(f"   Status: {r.status_code}")
    print("   Response:", r.json())
except Exception as e:
    print(f"   Error: {e}")

# Test memrag endpoint
print("\n4. Testing /memrag")
try:
    r = requests.get('http://localhost:8000/memrag')
    print(f"   Status: {r.status_code}")
    print("   Response:", json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"   Error: {e}")

# Test settings endpoint
print("\n5. Testing /settings")
try:
    r = requests.get('http://localhost:8000/settings')
    print(f"   Status: {r.status_code}")
    print("   Settings:", json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"   Error: {e}")

print("\n=== All Tests Completed ===")
