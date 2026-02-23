@echo off
REM Script para ejecutar el sistema de automatización de Git (sin mostrar consola)
cd /d "%~dp0"
call venv\Scripts\activate.bat
pythonw git_automation_gui.py
