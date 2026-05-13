@echo off
REM ============================================================================
REM FitControl Pro V2 - Setup automatico para Windows
REM since 2018 Ailson Soares
REM ============================================================================
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   FitControl Pro V2 - Setup Windows
echo ============================================================
echo.

REM --- 1. Verificar Python ---
where python >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado no PATH.
    echo Instale Python 3.10+ em https://www.python.org/downloads/
    echo Marque a opcao "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [OK] Python !PYVER! detectado.
echo.

REM --- 2. Criar virtualenv ---
if not exist ".venv\" (
    echo [1/6] Criando ambiente virtual .venv...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERRO] Falha ao criar .venv
        pause
        exit /b 1
    )
) else (
    echo [1/6] .venv ja existe, pulando.
)
echo.

REM --- 3. Ativar venv ---
echo [2/6] Ativando .venv...
call .venv\Scripts\activate.bat
echo.

REM --- 4. Atualizar pip ---
echo [3/6] Atualizando pip...
python -m pip install --upgrade pip --quiet
echo.

REM --- 5. Instalar dependencias core ---
echo [4/6] Instalando dependencias (pode levar 2-3 minutos)...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar requirements.txt
    pause
    exit /b 1
)
echo [OK] Dependencias core instaladas.
echo.

REM --- 6. Pergunta sobre WeasyPrint (PDFs) ---
echo [5/6] WeasyPrint para geracao de PDFs (opcional)
echo ------------------------------------------------------------
echo No Windows, o WeasyPrint precisa do GTK3 runtime.
echo Se voce ainda nao instalou o GTK3, baixe em:
echo   https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
echo.
set /p INSTALL_PDF="Deseja tentar instalar WeasyPrint agora? (s/N): "
if /i "!INSTALL_PDF!"=="s" (
    pip install -r requirements-pdf.txt
    if errorlevel 1 (
        echo [AVISO] WeasyPrint falhou - PDFs ficarao desabilitados
        echo         O app funciona normalmente, apenas a exportacao em PDF nao estara disponivel.
    ) else (
        echo [OK] WeasyPrint instalado.
    )
) else (
    echo [INFO] WeasyPrint pulado. PDFs ficarao desabilitados localmente.
    echo        Em producao Docker/Cloud, os PDFs funcionarao normalmente.
)
echo.

REM --- 7. Criar .env se nao existe ---
echo [6/6] Configurando .env...
if not exist ".env" (
    copy .env.example .env >nul
    echo [OK] .env criado a partir de .env.example
) else (
    echo [INFO] .env ja existe, mantendo configuracao atual.
)
echo.

REM --- 8. Aplicar migrations ---
echo Aplicando migracoes do banco (SQLite local)...
set FLASK_APP=app.py
flask db upgrade
if errorlevel 1 (
    echo [AVISO] Migrations falharam - tente manualmente: flask db upgrade
)
echo.

echo ============================================================
echo   Setup concluido!
echo ============================================================
echo.
echo Para iniciar o app:
echo   1. .venv\Scripts\activate
echo   2. python app.py
echo.
echo Ou simplesmente execute: run_windows.bat
echo.
echo Acesse: http://localhost:5000
echo.
pause
