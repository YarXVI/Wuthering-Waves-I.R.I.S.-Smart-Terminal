"""



"""
浼氳瘽瀛樺偍娴嬭瘯





"""



"""
import sys





import os





import json





import tempfile





import pytest





sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))





from agent_core.memory.session_store import _validate_tool_sequence





class TestSessionStore:





"""浼氳瘽瀛樺偍宸ュ叿鍑芥暟娴嬭瘯"""





def test_validate_tool_sequence_complete(self):





"""瀹屾暣鐨?tool_call 搴忓垪搴斾繚鎸佷笉鍙?""



"""
messages = [





{"role": "user", "content": "search files"},





{





"role": "assistant",





"content": "",





"tool_calls": [{"id": "call1", "type": "function", "function": {"name": "search", "arguments": "{}"}}],





},





{"role": "tool", "tool_call_id": "call1", "content": "result"},





{"role": "assistant", "content": "here are the results"},





]





cleaned = _validate_tool_sequence(messages)





assert len(cleaned) == len(messages)





def test_validate_tool_sequence_orphaned(self):





"""瀛ょ珛鐨?tool_call锛堟病鏈?tool 鍝嶅簲锛夊簲琚Щ闄?""



"""
messages = [





{"role": "user", "content": "search files"},





{





"role": "assistant",





"content": "",





"tool_calls": [{"id": "call1", "type": "function", "function": {"name": "search", "arguments": "{}"}}],





},





# 娌℃湁 tool 鍝嶅簲 鈥?搴旇绉婚櫎





{"role": "assistant", "content": "final answer"},





]





cleaned = _validate_tool_sequence(messages)





assert len(cleaned) == 2  # 鍙湁 user 鍜屾渶鍚庝竴涓?assistant





if __name__ == "__main__":





pytest.main(["-v", __file__])




