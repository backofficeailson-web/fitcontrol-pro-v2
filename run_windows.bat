@echo off
REM ============================================================================
REM FitControl Pro V2 - Iniciar app no Windows
REM since 2018 Ailson Soares
REM ============================================================================
setlocal

if not exist ".venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual nao encontrado.
    echo Execute primeiro: setup_windows.bat
    pause
    exit /b 1
)

echo Ativando ambiente virtual...
call .venv\Scripts\activate.bat

if not exist ".env" (
    echo [AVISO] .env nao encontrado, copiando do exemplo...
    copy .env.example .env >nul
)

set FLASK_APP=app.py
set FLASK_ENV=development

echo.
echo ============================================================
echo   FitControl Pro V2 iniciando...
echo   Acesse: http://localhost:5000
echo   Pressione CTRL+C para parar
echo ============================================================
echo.

python app.py
pause
