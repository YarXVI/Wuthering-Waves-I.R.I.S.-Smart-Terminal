#!/usr/bin/env python3

"""

I.R.I.S. Agent API Server

模块化路由加载 - 每个模块独立，一个挂了不影响其他

"""



import sys

import os



sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from fastapi.staticfiles import StaticFiles

from fastapi.responses import FileResponse

from agent_core.config import config

from agent_core.core.agent_manager import manager

from agent_core.utils.isolation import safe_import

import uvicorn



app = FastAPI(title="I.R.I.S. Agent API", version="0.4.0")





@app.on_event("startup")

async def startup_event():

    """启动时初始化"""

    from server.ws_manager import manager as ws_manager

    ws_manager.start_cleanup()

    print("  [OK] ws cleanup       - WebSocket cleanup started")





app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)



# ============================================================

# 模块化路由注册 - 每个模块独立加载

# 一个路由模块挂了不影响其他，服务器照常启动

# ============================================================



ROUTER_MODULES = [
    ("chat", "Chat & Agent Management"),
    ("memory", "Memory Management"),
    ("memrag", "MemRAG Memory Enhancement"),
    ("settings", "Settings & Service Management"),
    ("skills", "Skills Management"),
    ("collaboration", "Agent Collaboration"),
    ("whiteboard", "Project Room Whiteboard"),
    ("agents", "Custom Agent Management"),
    ("meetings", "Smart Meeting Room"),
    ("workflows", "Workflow Management"),
    ("ws", "WebSocket Real-time Whiteboard"),
    ("notification_ws", "Notification WebSocket"),
]



loaded = 0

failed = 0



for module_name, description in ROUTER_MODULES:

    mod = safe_import(f"server.routers.{module_name}")

    if mod and hasattr(mod, "router"):

        app.include_router(mod.router, prefix="")

        loaded += 1

        print(f"  [OK] {module_name:15s} - {description}")

    else:

        failed += 1

        print(f"  [--] {module_name:15s} - {description} (NOT LOADED)")





# ============================================================

# 实时广播钩子

# ============================================================



def _register_broadcast_hook():

    """注册实时广播钩子，让 auto_discuss 每轮即时推送"""

    from agent_core.project_room.meeting import set_on_round_complete

    from server.ws_manager import manager as ws_manager

    from server._async_utils import fire_and_forget



    def _on_round(room_id: str, round_data: dict):

        fire_and_forget(ws_manager.broadcast(room_id, {

            "type": "round_added",

            "round": round_data,

            "current_round": round_data.get("round_number", 0),

        }))



    set_on_round_complete(_on_round)

    print("  [OK] broadcast hook    - Real-time broadcast activated")





# ============================================================

# 基础端点

# ============================================================



@app.get("/")

def root():

    return {

        "name": "I.R.I.S. Agent API",

        "version": "0.4.0",

        "modules": {"loaded": loaded, "failed": failed},

        "frontend": "Run the desktop app in the desktop folder",

    }





@app.get("/health")

def health():

    return {"status": "ok", "model": config.openai_model}





# ============================================================

# 入口点

# ============================================================



def main():

    if not config.is_valid:

        print("[WARN] OPENAI_API_KEY not configured - some features may not work")

        print("       Set it in .env or via the Settings UI")



    # 注册实时广播钩子（每轮讨论即时推送）

    _register_broadcast_hook()



    port = int(os.getenv("AGENT_PORT", "8000"))

    print(f"\nI.R.I.S. Agent API v0.4.0 - http://127.0.0.1:{port}")

    print(f"Model: {config.openai_model}")

    print(f"Router modules: {loaded} loaded, {failed} failed")

    print(f"Agents: {len(manager.list_agents())}")

    for a in manager.list_agents():

        print(f"  - {a['name']} ({a['id']}) [{a.get('title', 'no title')}]")

    print()

    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")





if __name__ == "__main__":

    main()

