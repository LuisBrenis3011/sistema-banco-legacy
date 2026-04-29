@echo off
echo Iniciando Sistema Core Banco Legacy...

start "Sistema Legacy" cmd /k "cd /d %~dp0 && venv\Scripts\activate && py app_legacy.py"

echo Listo. El sistema legacy esta corriendo.