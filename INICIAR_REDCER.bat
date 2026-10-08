@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo REDCER no esta instalado todavia.
  echo Ejecuta primero INSTALAR_REDCER.bat
  pause
  exit /b 1
)
call ".venv\Scripts\activate.bat"
start "REDCER WEB" http://127.0.0.1:5000
python app.py
pause
