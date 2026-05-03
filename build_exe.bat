@echo off
chcp 65001 >nul
title Aimis-Build

echo ============================================
echo   Building Aimis Launcher EXE
echo ============================================
echo.

:: 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

:: 清理旧构建
if exist "dist\launcher" rmdir /s /q "dist\launcher"
if exist "build\launcher" rmdir /s /q "build\launcher"

:: 打包
echo Building...
pyinstaller --onefile --console --name "Aimis Launcher" launcher.py

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed.
    pause & exit /b 1
)

echo.
echo ============================================
echo   Build complete!
echo   EXE: dist\Aimis Launcher.exe
echo   Size:
for %%f in ("dist\Aimis Launcher.exe") do echo   %%~zf bytes
echo ============================================
echo.
echo   Note: The EXE bundles Python but the project
echo   dependencies (fastapi, openai, etc.) must
echo   still be installed via pip.
echo.
pause
