@echo off
title Pendencias Scheduler

REM Verificar se o executável existe
if not exist "PendenciasScheduler.exe" (
    echo Erro: PendenciasScheduler.exe nao encontrado!
    echo.
    echo Por favor, execute build.bat primeiro para gerar o executavel.
    pause
    exit /b 1
)

REM Verificar se o arquivo .env existe
if not exist ".env" (
    echo Aviso: Arquivo .env nao encontrado!
    echo.
    echo O scheduler pode nao funcionar corretamente sem as configuracoes.
    echo Deseja continuar mesmo assim? (S/N)
    choice /c SN /n /m ""
    if errorlevel 2 exit /b 0
)

echo ====================================
echo  Iniciando Pendencias Scheduler
echo ====================================
echo.
echo Pressione Ctrl+C para parar
echo.

REM Executar o scheduler
PendenciasScheduler.exe

if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo  Erro ao executar o scheduler!
    echo ====================================
    echo.
    pause
)
