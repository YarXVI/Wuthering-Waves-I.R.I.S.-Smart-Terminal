@echo off
REM ============================================
REM I.R.I.S. - Virtual Office - Launcher
REM ============================================

title I.R.I.S. - Virtual Office

cd /d "%~dp0"

echo.
echo   I.R.I.S. - Virtual Office
echo.
echo [1] Launch Dev Mode (API + Vite)
echo [2] Launch Packaged exe (if exists)
echo [3] Launch API Server only
echo.
echo [0] Exit
echo.
echo ============================================
set /p choice=Choose [1-3]:

if "%choice%"=="1" goto dev
if "%choice%"=="2" goto packaged
if "%choice%"=="3" goto api
if "%choice%"=="0" exit

:dev
echo Starting Development Mode...
start cmd /k "python -m server.main"
start cmd /k "cd desktop && npm run dev"
goto end

:packaged
echo Starting Packaged Application...
if exist "dist\iris.exe" (
    start "" "dist\iris.exe"
) else (
    echo Packaged application not found. Please run build first.
)
goto end

:api
echo Starting API Server Only...
python -m server.main
goto end

:end
pause
