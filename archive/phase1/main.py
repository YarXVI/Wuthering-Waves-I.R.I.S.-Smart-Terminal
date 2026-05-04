#!/usr/bin/env python3
"""
Phase 1 — 命令行原型
验证 AI 核心（大脑）能否独立工作。
"""

import sys, signal
from agent_core.config import config
from agent_core.core.agent import Agent


def sanitize_text(text: str) -> str:
    encoding = sys.stdout.encoding or "utf-8"
    try:
        text.encode(encoding)
        return text
    except UnicodeEncodeError:
        pass
    cleaned = []
    for ch in text:
        try:
            ch.encode(encoding)
            cleaned.append(ch)
        except UnicodeEncodeError:
            cleaned.append("")
    return "".join(cleaned)


signal.signal(signal.SIGINT, lambda s, f: (print("\n\n再见！"), sys.exit(0)))

if not config.is_valid:
    print("[错误] 未配置 OPENAI_API_KEY")
    sys.exit(1)

print("=" * 56)
print(f"  爱弥斯 Agent 核心 . Phase 1")
print(f"  办公区: {config.notes_dir}")
print(f"  模型: {config.openai_model}")
print("=" * 56)

agent = Agent()
while True:
    try:
        inp = input("\n[你说]: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\n再见！")
        break
    if not inp:
        continue
    if inp.lower() in ("/quit", "/exit", "/q"):
        break
    if inp.lower() == "/reset":
        agent.reset()
        print("[对话已重置]")
        continue

    print("[爱弥斯思考中...]")
    try:
        resp = agent.run(inp)
        print(f"\n[爱弥斯]:\n{sanitize_text(resp)}")
    except Exception as e:
        print(f"[出错]: {e}")
