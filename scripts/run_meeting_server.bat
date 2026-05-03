@echo off
chcp 65001 >nul
title Aimis-Meeting
cd /d "%~dp0.."

echo ============================================
echo   Aimis Meeting Server (standalone)
echo ============================================
echo.
echo  Frontend: http://127.0.0.1:8765/meeting
echo.
echo  Attach agents by calling:
echo    POST /meetings/suggest-agents  {"topic": "..."}
echo    POST /meetings/start           {"topic": "...", "agents": [...]}
echo.
echo  WebSocket:
echo    ws://127.0.0.1:8765/ws/{room_id}
echo.
echo ============================================
echo.

python -m server.meeting_server

pause
