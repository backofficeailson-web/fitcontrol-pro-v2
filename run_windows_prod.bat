@echo off
REM ============================================================================
REM FitControl Pro V2 - Iniciar em modo PRODUCAO no Windows usando Waitress
REM (Gunicorn nao roda em Windows; Waitress e o equivalente nativo Windows)
REM ============================================================================
setlocal

if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado.
    echo Execute primeiro: setup_windows.bat
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

if not exist ".env" copy .env.example .env >nul

REM Gerar SECRET_KEY forte se nao houver
if "%SECRET_KEY%"=="" (
    for /f "delims=" %%i in ('python -c "import secrets; print(secrets.token_urlsafe(48))"') do set SECRET_KEY=%%i
)
if "%WTF_CSRF_SECRET_KEY%"=="" set WTF_CSRF_SECRET_KEY=%SECRET_KEY%

set FLASK_APP=wsgi.py
set FLASK_ENV=production
set SESSION_COOKIE_SECURE=False
set LOG_TO_STDOUT=True

echo.
echo ============================================================
echo   FitControl Pro V2 - PRODUCAO (Waitress)
echo   Acesse: http://localhost:5000
echo ============================================================
echo.

python -m waitress --listen=0.0.0.0:5000 --threads=8 wsgi:app
pause
