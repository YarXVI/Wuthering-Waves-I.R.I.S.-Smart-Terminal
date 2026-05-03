@echo off
REM ============================================
REM Aimis - Build Script
REM 1. Build Frontend (Vite)
REM 2. Build Backend (PyInstaller)
REM 3. Build Electron App (Optional)
REM ============================================

title Aimis - Build Script
cd /d "%~dp0"

echo.
echo ============================================
echo   Aimis - Full Build Process
echo ============================================
echo.

REM Check Node.js
where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found! Please install Node.js first.
    pause
    exit /b 1
)

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b 1
)

echo [1/4] Install Dependencies...
echo.

cd desktop
if not exist "node_modules" (
    echo Installing desktop dependencies...
    call npm install
)
cd ..

echo.
echo [2/4] Build Frontend (Vite)...
echo.

cd desktop
call npm run build
if errorlevel 1 (
    echo [ERROR] Frontend build failed!
    pause
    exit /b 1
)
cd ..

echo.
echo [3/4] Pack Backend (PyInstaller)...
echo.

REM Check PyInstaller
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

python -m PyInstaller build_launcher.spec --clean
if errorlevel 1 (
    echo [ERROR] Backend packing failed!
    pause
    exit /b 1
)

echo.
echo [4/4] Build Electron App (Optional)...
echo.
choice /C YN /M "Continue building Electron app"
if errorlevel 2 goto done

cd desktop
if not exist "node_modules" (
    echo Installing desktop dependencies...
    call npm install
)

REM Make sure electron-builder is installed
npm list electron-builder >nul 2>&1
if errorlevel 1 (
    echo Installing electron-builder...
    npm install --save-dev electron-builder
)

call npm run electron:build
if errorlevel 1 (
    echo [ERROR] Electron build failed!
)
cd ..

:done
echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Output Files:
echo   - dist\Aimis.exe              (Standalone Launcher)
echo   - desktop\build\              (Electron App)
echo.
pause
