@echo off
cd /d "%~dp0ux-recruitment-bot"
"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -ExecutionPolicy Bypass -NoExit -File "%cd%\start.ps1"
