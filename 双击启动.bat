@echo off
chcp 65001
title 公众号招募工作台
cd /d "%~dp0ux-recruitment-bot"
%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -NoExit -File "%cd%\start.ps1"
