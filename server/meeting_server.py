"""
========== Standalone Meeting Server ==========

Loads only meeting + whiteboard + agent list routes, no Chat/MCP/Skills modules.

Usage: python server/meeting_server.py

Listens on: http://127.0.0.1:8000
Frontend access: http://127.0.0.1:8000/meeting

Or open desktop/meeting_standalone.html
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path
from agent_core.config import config
from agent_core.utils.isolation import safe_import

app = FastAPI(title="iris Meeting Server", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load only meeting-related routers
MEETING_ROUTERS = [
    ("meetings", "Smart Meeting Room"),
    ("whiteboard", "Shared Whiteboard"),
    ("agents", "Agent List (read-only)"),
    ("ws", "WebSocket Real-time Whiteboard"),
    ("notification_ws", "Notification WebSocket"),
]

loaded = 0
failed = 0
for module_name, description in MEETING_ROUTERS:
    mod = safe_import(f"server.routers.{module_name}")
    if mod and hasattr(mod, "router"):
        app.include_router(mod.router, prefix="")
        loaded += 1
        print(f"  [OK] {module_name:15s} - {description}")
    else:
        failed += 1
        print(f"  [--] {module_name:15s} - {description} (NOT LOADED)")

# Static pages
STATIC_DIR = Path(__file__).parent.parent / "desktop"

@app.get("/")
def root():
    return {
        "name": "iris Meeting Server",
        "version": "0.1.0",
        "routers": {"loaded": loaded, "failed": failed},
        "frontend": "Open /meeting or open desktop/meeting_standalone.html",
    }

@app.get("/health")
def health():
    return {"status": "ok", "model": config.openai_model}

@app.get("/meeting")
def meeting_page():
    """Standalone meeting frontend page"""
    html_path = STATIC_DIR / "meeting_standalone.html"
    if html_path.exists():
        return FileResponse(str(html_path))
    return {"error": "meeting_standalone.html not found"}

def main():
    if not config.is_valid:
        print("[WARN] OPENAI_API_KEY not configured")

    port = int(os.getenv("AGENT_PORT", "8000"))

    from agent_core.project_room.meeting import set_on_round_complete
    from server.ws_manager import manager as ws_manager
    from server._async_utils import fire_and_forget

    def _on_round(room_id: str, round_data: dict):
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon_threadsafe(
                lambda: ws_manager.broadcast_to_room(room_id, round_data)
            )
        except Exception:
            pass

    set_on_round_complete(_on_round)

    import uvicorn
    print(f"\nI.R.I.S. Meeting Server - http://127.0.0.1:{port}")
    print(f"Frontend: http://127.0.0.1:{port}/meeting")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()
