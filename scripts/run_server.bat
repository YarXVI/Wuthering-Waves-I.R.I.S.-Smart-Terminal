@echo off
chcp 65001 >nul
title Aimis-API
cd /d "%~dp0.."
python -m server.main
pause
