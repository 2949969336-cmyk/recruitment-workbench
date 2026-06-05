@echo off
chcp 65001 >nul
title 公众号招募工作台
cd /d "%~dp0ux-recruitment-bot"
powershell -ExecutionPolicy Bypass -NoExit -File ".\start.ps1"
