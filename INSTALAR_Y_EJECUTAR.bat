@echo off
cd /d "%~dp0"
where py >nul 2>&1 && set PY=py || set PY=python
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
call .venv\Scripts\activate
python -m pip install -r requirements.txt
python app.py
pause
