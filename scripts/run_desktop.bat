@echo off
chcp 65001 >nul
title Aimis-Desktop
cd /d "%~dp0..\desktop"
if not exist node_modules npm install
npm run electron:dev
pause
