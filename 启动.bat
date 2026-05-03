@echo off
REM ============================================
REM Aimis - Virtual Office - Launcher
REM ============================================

title Aimis - Virtual Office

cd /d "%~dp0"

echo.
echo   Aimis - Virtual Office
echo.
echo [1] Launch Dev Mode (API + Vite)
echo [2] Launch Packaged exe (if exists)
echo [3] Launch API Server only
echo.
echo [0] Exit
echo.
echo ============================================
set /p choice=Choose [1-3]:

if "%choice%"=="1" (
    echo Launching Dev Mode...
    python launcher.py
) else if "%choice%"=="2" (
    if exist "dist\Aimis.exe" (
        echo Launching Aimis.exe...
        start "" "dist\Aimis.exe"
    ) else (
        echo dist\Aimis.exe not found!
        echo Please run the build script first, or choose 1.
        pause
    )
) else if "%choice%"=="3" (
    echo Launching API Server...
    python -m server.main
) else if "%choice%"=="0" (
    exit
) else (
    echo Invalid choice!
    pause
)
