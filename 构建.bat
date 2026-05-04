@echo off
REM ============================================
REM I.R.I.S. Build Script
REM 1. Build Frontend (Vite)
REM 2. Build Backend (PyInstaller)
REM 3. Build Electron App (Optional)
REM ============================================

title I.R.I.S. - Build Script
cd /d "%~dp0"

echo.
echo ============================================
echo   I.R.I.S. - Full Build Process
echo ============================================
echo.

REM Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [1/4] Installing frontend dependencies...
cd desktop
call npm install
if errorlevel 1 (
    echo Error: npm install failed
    pause
    exit /b 1
)

echo [2/4] Building frontend...
call npm run build
if errorlevel 1 (
    echo Error: Frontend build failed
    pause
    exit /b 1
)
cd ..

echo [3/4] Installing backend dependencies...
pip install -r agent_core\requirements.txt
pip install pyinstaller
if errorlevel 1 (
    echo Error: Backend dependencies installation failed
    pause
    exit /b 1
)

echo [4/4] Building backend executable...
pyinstaller build_launcher.spec
if errorlevel 1 (
    echo Error: Backend build failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Output: dist\iris.exe
echo.
pause
