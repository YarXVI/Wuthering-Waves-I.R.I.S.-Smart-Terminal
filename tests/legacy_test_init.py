"""Quick integration test for agents API"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_core.core.agent_manager import manager
from agent_core.core.agent_store import load_agents, save_agents, generate_agent_id
from agent_core.core.agent_profile import AgentProfile

# Test 1: generate_agent_id
print("=== ID Generation ===")
print(f"  剪辑�?-> {generate_agent_id('剪辑�?)}")
print(f"  视频剪辑助手 -> {generate_agent_id('视频剪辑助手')}")
print(f"  Video Editor -> {generate_agent_id('Video Editor')}")
print(f"  My Agent 007 -> {generate_agent_id('My Agent 007')}")

# Test 2: save and load a custom agent
print("\n=== Save & Load ===")
profile = AgentProfile(
    id="剪辑�?,
    name="剪辑�?,
    emoji="🎬",
    title="视频剪辑�?,
    specialty="视频脚本、分镜设计、内容策划、剪辑特�?,
    system_prompt="你叫「剪辑师」，是办公室的视频制作专家�?,
    tool_names=["search_local_files", "read_file_content", "call_agent"],
)
agents = load_agents()
agents["剪辑�?] = profile
save_agents(agents)
print(f"  Saved. Total: {len(agents)}")

reloaded = load_agents()
print(f"  Reloaded. Total: {len(reloaded)}")
for aid, p in reloaded.items():
    print(f"    {aid}: {p.name} [{p.specialty[:30]}]")

# Test 3: confirm iris is still there
assert "iris" in reloaded, "iris must exist"
print("\n  iris specialty:", reloaded["iris"].specialty)

# Cleanup: remove test agent
agents = load_agents()
agents.pop("剪辑�?, None)
save_agents(agents)
print("\n  Cleaned up test agent")

# Test 4: promote 剪辑�?to run manager
print("\n=== Manager registration ===")
manager.register_agent(profile)
print(f"  Manager agents: {len(manager.profiles)}")
for aid, p in manager.profiles.items():
    print(f"    {aid}: {p.name} [{p.title}]")

# Test manager colleague context
ctx = manager._build_colleague_context("iris")
assert "剪辑�? in ctx, "colleague context should include 剪辑�?
print(f"\n  Colleague context for iris:\n{ctx[:300]}...")

# Clean up manager
manager.unregister_agent("剪辑�?)
print(f"\n  After unregister: {len(manager.profiles)} agents")

print("\n=== ALL TESTS PASSED ===")
