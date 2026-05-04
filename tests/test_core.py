"""



"""
Agent 核心单元测试





"""



"""
import sys





import os





import pytest





sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))





from agent_core.core.agent_profile import AgentProfile, AgentStatus, DEFAULT_AGENTS





from agent_core.core.agent_store import generate_agent_id, _to_dict, _from_dict





from agent_core.utils.text import strip_emoji, sanitize_message, sanitize_messages





class TestAgentProfile:





"""AgentProfile 数据模型测试"""





def test_default_agents_exist(self):





assert "iris" in DEFAULT_AGENTS





assert "codey" in DEFAULT_AGENTS





assert "scribe" in DEFAULT_AGENTS





def test_agent_profile_creation(self):





profile = AgentProfile(





id="test-agent",





name="测试?,





emoji="🧪",





title="测试助手",





specialty="单元测试、集成测?,





system_prompt="你是一个测试助手?,





tool_names=["search_local_files"],





)





assert profile.id == "test-agent"





assert profile.name == "测试?





assert profile.status == AgentStatus.IDLE





assert profile.message_count == 0





def test_agent_status_enum(self):





assert AgentStatus.IDLE.value == "idle"





assert AgentStatus.THINKING.value == "thinking"





assert AgentStatus.WORKING.value == "working"





assert AgentStatus.ERROR.value == "error"





class TestAgentStore:





"""Agent 存储工具测试"""





def test_generate_agent_id_chinese(self):





assert generate_agent_id("剪辑?) == "剪辑?





def test_generate_agent_id_latin(self):





# 空格会被移除（不在允许字符集内），然后转小写





assert generate_agent_id("Video Editor") == "videoeditor"





def test_generate_agent_id_mixed(self):





# 空格和数字会被保留，转小?        result = generate_agent_id("My Agent 007")





assert "my" in result





assert "agent" in result





assert "007" in result





assert " " not in result





def test_generate_agent_id_empty(self):





assert generate_agent_id("") == "custom_agent"





def test_generate_agent_id_truncate(self):





long_name = "a" * 50





assert len(generate_agent_id(long_name)) <= 32





def test_to_dict_excludes_runtime_fields(self):





profile = AgentProfile(id="t", name="Test", emoji="🧪", title="Tester")





d = _to_dict(profile)





assert "status" not in d





assert "current_task" not in d





assert "message_count" not in d





def test_from_dict_roundtrip(self):





original = AgentProfile(





id="roundtrip",





name="往返测?,





emoji="🔄",





title="测试",





specialty="测试",





system_prompt="测试提示?,





tool_names=["search_local_files", "read_file_content"],





)





d = _to_dict(original)





restored = _from_dict(d)





assert restored.id == original.id





assert restored.name == original.name





assert restored.tool_names == original.tool_names





class TestTextUtils:





"""文本工具函数测试"""





def test_strip_emoji_removes_emoji(self):





assert "hello" == strip_emoji("hello?).strip()





assert "test" == strip_emoji("✅test?)





def test_strip_emoji_preserves_chinese(self):





result = strip_emoji("你好世界")





assert "你好世界" in result





def test_sanitize_message_keeps_allowed_fields(self):





msg = {"role": "user", "content": "hello", "reasoning_content": "thinking..."}





clean = sanitize_message(msg)





assert "role" in clean





assert "content" in clean





assert "reasoning_content" not in clean





def test_sanitize_messages_removes_reasoning(self):





msgs = [





{"role": "user", "content": "hi"},





{"role": "assistant", "content": "hello?, "reasoning_content": "think"},





]





clean = sanitize_messages(msgs)





assert len(clean) == 2





assert "reasoning_content" not in clean[1]





assert "? not in clean[1]["content"]





if __name__ == "__main__":





pytest.main(["-v", __file__])




