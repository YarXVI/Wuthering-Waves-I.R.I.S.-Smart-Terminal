@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================
echo   Aimis - Virtual Office
echo ============================================
echo.

:: 检查 .env
if not exist ".env" (
    echo [ERROR] .env not found
    pause & exit /b 1
)

:: 强制杀端口（API 8765 + Vite 5173）
echo [1/3] Cleaning ports...
for %%p in (8765 5173) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| find "%%p"') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)
timeout /t 1 >nul

:: 启动 API
echo [2/3] Starting API server...
start "Aimis-API" cmd /c "python -m server.main"
echo   API: http://127.0.0.1:8765

:: 等待就绪
echo   Waiting...
:WAIT
timeout /t 2 >nul
curl -s http://127.0.0.1:8765/health >nul 2>&1 || goto WAIT
echo   API Ready.

:: 启动前端
echo [3/3] Starting desktop...
start "Aimis-Desktop" cmd /c "cd /d desktop && npm run electron:dev"
echo   Desktop: http://localhost:5173

cls
echo.
echo ============================================
echo   ALL SERVICES STARTED
echo.
echo   API:  http://127.0.0.1:8765
echo   Web:  http://localhost:5173
echo   Key:  Alt+Space
echo.
echo   [Close window = Stop all]
echo ============================================
echo.

pause >nul

:: 清理
echo Stopping...
taskkill /f /fi "WINDOWTITLE eq Aimis-API" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Aimis-Desktop" >nul 2>&1
for %%p in (8765 5173) do (
    for /f "tokens=5" %%a in ('netstat -aon ^| find "%%p"') do (
        taskkill /f /pid %%a >nul 2>&1
    )
)
echo All stopped.
timeout /t 2 >nul
