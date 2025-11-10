@echo off
echo ====================================
echo  Construindo Scheduler Executavel
echo ====================================
echo.

REM Verificar se PyInstaller está instalado
python -c "import PyInstaller" 2>nul
if %errorlevel% neq 0 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
)

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist *.spec del /q *.spec

echo.
echo Construindo executavel...
pyinstaller --name=PendenciasScheduler ^
    --onefile ^
    --console ^
    --icon=NONE ^
    --add-data ".env;." ^
    --hidden-import=pyodbc ^
    --hidden-import=schedule ^
    --hidden-import=pandas ^
    --hidden-import=dotenv ^
    --hidden-import=app.services.pendencias ^
    --hidden-import=app.services.database ^
    --hidden-import=app.models ^
    --hidden-import=app.core ^
    --hidden-import=app.utils ^
    --collect-all schedule ^
    --collect-all pyodbc ^
    --collect-all pandas ^
    app.py

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo  Build concluido com sucesso!
    echo ====================================
    echo.
    echo O executavel esta em: dist\PendenciasScheduler.exe
    echo.
    echo Para executar:
    echo   1. Copie o arquivo .env para a pasta do executavel
    echo   2. Execute: dist\PendenciasScheduler.exe
    echo.
) else (
    echo.
    echo ====================================
    echo  Erro durante o build!
    echo ====================================
    echo.
)

pause
