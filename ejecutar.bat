@echo off
REM Script para ejecutar el sistema de automatización de Git
cd /d "%~dp0"
call venv\Scripts\activate.bat
python git_automation_gui.py
pause
