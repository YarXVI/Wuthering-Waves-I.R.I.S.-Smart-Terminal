"""
========== 会议模块独立测试脚本 ==========
连接到已运行�?API 服务器，验证会议全流程�?
用法:
  python test_meeting_standalone.py [port]

  默认连接 http://127.0.0.1:8765
  可指定端�? python test_meeting_standalone.py 8766
"""
import sys, os, json, time, urllib.request, urllib.parse, subprocess, re

# GBK 兼容打印：去�?emoji
def _safe(text):
    if not isinstance(text, str):
        text = str(text)
    return re.sub(r'[^\x20-\x7E\u4e00-\u9fff\u3000-\u303f\uff00-\uffef\n\r\t]', '?', text)

def p(*args, **kwargs):
    print(*[_safe(a) for a in args], **kwargs)

port = sys.argv[1] if len(sys.argv) > 1 else "8765"
BASE = f"http://127.0.0.1:{port}"

def api(path, data=None, method="GET"):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data and method != "GET" else None
    req = urllib.request.Request(url, method=method, data=body,
        headers={"Content-Type": "application/json"} if data else {})
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": e.code, "detail": e.read().decode()[:200]}

def test_all():
    p("=", 60)
    p("会议模块测试 (port %s)" % port)
    p("=", 60)

    # 1. Health
    r = api("/health")
    p("\n[1/5] 健康检�?", r)
    assert r.get("status") == "ok", "Health check failed"

    # 2. List agents
    r = api("/agents")
    agents = r.get("agents", [])
    p("\n[2/5] 可用同事 (%d �?:" % len(agents))
    for a in agents:
        p("  %s (%s) - %s" % (a.get("name"), a.get("id"), a.get("title")))

    # 3. Suggest meeting agents
    r = api("/meetings/suggest-agents",
        {"topic": "讨论系统架构选型 Python 后端�?FastAPI 还是 Flask"},
        method="POST")
    p("\n[3/5] 议题匹配建议:", r)
    suggested = r.get("suggested", [])
    p("  推荐参会:", suggested)

    # 4. Create meeting & auto discuss
    participants = suggested or ["codey", "scribe"]
    r = api("/meetings/start",
        {"topic": "系统架构技术选型讨论", "agents": participants},
        method="POST")
    room_id = r.get("room_id")
    p("\n[4/5] 创建会议: room_id=%s, status=%s" % (room_id, r.get("status")))
    assert room_id, "Create meeting failed"

    p("\n  自动讨论执行�?(最�?4 �? 可能需 30-60 �?...")
    t0 = time.time()
    r = api("/meetings/%s/auto-discuss?max_rounds=4" % room_id, method="POST")
    elapsed = time.time() - t0
    p("  耗时: %.1fs" % elapsed)
    p("  完成轮次: %s" % r.get("rounds_completed"))
    p("  共识: %s" % r.get("consensus"))
    p("  状�? %s" % r.get("message"))

    # View discussion
    r = api("/meetings/%s" % room_id)
    rounds = r.get("rounds", [])
    p("\n  讨论记录 (%d �?:" % len(rounds))
    for rd in rounds:
        content = rd.get("content", "")
        p("  �?d�?%s (%s): %s" % (
            rd.get("round_number"), rd.get("author"),
            rd.get("type"), content[:150] if len(content) > 150 else content))

    # 5. Summary
    p("\n[5/5] 生成会议纪要...")
    r = api("/meetings/%s/judge" % room_id, method="POST")
    p("  共识判断:", r)
    r = api("/meetings/%s/summarize" % room_id, method="POST")
    p("  会议纪要:")
    p("    主题:", r.get("topic"))
    p("    参与�?", r.get("participants"))
    p("    决策:", r.get("decisions"))
    p("    待办:", r.get("action_items"))
    p("    总结:", r.get("summary"))

    p("\n", "=", 60)
    p("全部测试完成" if room_id else "测试失败")
    p("=", 60)

if __name__ == "__main__":
    test_all()
