"""



"""
会议模块单元测试 ?测试数据模型、轮次调度、持久化





"""



"""
import sys





import os





import json





import tempfile





import pytest





from pathlib import Path





from datetime import datetime





sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))





from agent_core.project_room.meeting import MeetingSession, Round





from agent_core.project_room.whiteboard import Whiteboard, EntryType, WhiteboardEntry





class TestMeetingModel:





"""MeetingSession 数据模型测试"""





def test_round_creation(self):





r = Round(round_number=1, author="iris", content="讨论开?)





assert r.round_number == 1





assert r.author == "iris"





assert r.type == "discussion"





assert r.timestamp > 0





def test_round_to_dict(self):





r = Round(round_number=1, author="codey", content="方案一", type="proposal")





d = r.to_dict()





assert d["round_number"] == 1





assert d["author"] == "codey"





assert d["type"] == "proposal"





def test_meeting_creation(self):





m = MeetingSession(





room_id="test_001",





topic="架构讨论",





agents=["codey", "scribe"],





)





assert m.room_id == "test_001"





assert m.status == "discussing"





assert m.consensus is False





assert len(m.rounds) == 0





def test_meeting_to_dict(self):





m = MeetingSession(room_id="t1", topic="测试", agents=["codey"])





m.rounds.append(Round(round_number=1, author="codey", content="hello"))





d = m.to_dict()





assert d["room_id"] == "t1"





assert len(d["rounds"]) == 1





def test_next_speaker_round1(self):





"""第一轮：第一?specialist 发言"""





m = MeetingSession(room_id="t", topic="t", agents=["codey", "scribe"])





speaker1 = m.next_speaker()





# Round 1: 第一?agent





assert speaker1 == "codey"





def test_next_speaker_round2(self):





"""第二轮：第二?specialist"""





m = MeetingSession(room_id="t", topic="t", agents=["codey", "scribe"])





m.rounds.append(Round(round_number=1, author="codey", content="提案"))





speaker2 = m.next_speaker()





assert speaker2 == "scribe"





def test_next_speaker_round_iris(self):





"""所?specialist 说完后，iris 评审"""





m = MeetingSession(room_id="t", topic="t", agents=["codey"])





m.rounds.append(Round(round_number=1, author="codey", content="提案"))





# Round 2: 轮到 iris





speaker2 = m.next_speaker()





assert speaker2 == "iris"





def test_current_round(self):





m = MeetingSession(room_id="t", topic="t", agents=[])





assert m.current_round == 1





m.rounds.append(Round(round_number=1, author="a", content="x"))





assert m.current_round == 2





class TestWhiteboard:





"""白板模型测试"""





def test_add_entry(self):





wb = Whiteboard(room_id="test_room")





entry = wb.add("iris", EntryType.DECISION, "使用 Python")





assert entry.author == "iris"





assert entry.type == EntryType.DECISION





assert entry.content == "使用 Python"





assert entry.resolved is True





def test_add_issue_unresolved(self):





wb = Whiteboard(room_id="test")





entry = wb.add("codey", EntryType.ISSUE, "?Bug")





assert entry.resolved is False





def test_add_task_unresolved(self):





wb = Whiteboard(room_id="test")





entry = wb.add("scribe", EntryType.TASK, "写文?)





assert entry.resolved is False





def test_get_by_type(self):





wb = Whiteboard(room_id="test")





wb.add("a", EntryType.DECISION, "d1")





wb.add("b", EntryType.DECISION, "d2")





wb.add("c", EntryType.NOTE, "n1")





assert len(wb.get_by_type(EntryType.DECISION)) == 2





assert len(wb.get_by_type(EntryType.NOTE)) == 1





def test_search(self):





wb = Whiteboard(room_id="test")





wb.add("a", EntryType.NOTE, "数据库选型")





wb.add("b", EntryType.NOTE, "前端框架")





assert len(wb.search("数据?)) == 1





assert len(wb.search("框架")) == 1





def test_resolve_issue(self):





wb = Whiteboard(room_id="test")





entry = wb.add("a", EntryType.ISSUE, "问题1", resolved=False)





assert wb.resolve_issue(entry.entry_id) is True





assert wb.get(entry.entry_id).resolved is True





def test_unresolved_issues(self):





wb = Whiteboard(room_id="test")





wb.add("a", EntryType.ISSUE, "问题1", resolved=False)





wb.add("b", EntryType.ISSUE, "问题2", resolved=True)  # 显式标记为已解决





assert len(wb.get_unresolved_issues()) == 1





def test_summarize(self):





wb = Whiteboard(room_id="test")





wb.add("a", EntryType.DECISION, "决策内容")





summary = wb.summarize()





assert "项目白板" in summary





assert "决策" in summary





def test_save_and_load(self):





wb = Whiteboard(room_id="test_save_load")





wb.add("iris", EntryType.DECISION, "测试持久?)





wb.save()





wb2 = Whiteboard(room_id="test_save_load")





wb2.load()





assert len(wb2.entries) >= 1





assert wb2.entries[-1].content == "测试持久?





# 清理测试数据





wb.storage_path.unlink(missing_ok=True)





if __name__ == "__main__":





pytest.main(["-v", __file__])




