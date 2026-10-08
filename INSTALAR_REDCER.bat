@echo off
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (set PY=py) else (set PY=python)
%PY% -m venv .venv
if errorlevel 1 (
 echo No se pudo crear el entorno de Python. Verifica que Python este instalado.
 pause
 exit /b 1
)
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if errorlevel 1 (
 echo No se pudieron instalar las dependencias.
 pause
 exit /b 1
)
echo.
echo Instalacion terminada.
echo Ahora puedes ejecutar INICIAR_REDCER.bat
pause
