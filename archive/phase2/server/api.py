"""FastAPI 服务器 — 桌面壳的后端 API"""
import sys
import os

# 确保 phase2 在 import path 中
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server.agent import Agent
from server.config import config

app = FastAPI(title="爱弥斯 Agent API", version="0.2.0")

# CORS — 允许 Tauri 前端跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["tauri://localhost", "http://localhost:1420", "https://tauri.localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局 Agent 实例（保持对话上下文）
agent = Agent()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@app.get("/health")
def health():
    return {"status": "ok", "model": config.openai_model, "notes_dir": config.notes_dir}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = agent.run(req.message)
    return ChatResponse(response=result)


@app.post("/api/reset")
def reset():
    agent.reset()
    return {"status": "ok"}
