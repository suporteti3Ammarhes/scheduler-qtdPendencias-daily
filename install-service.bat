@echo off
REM ====================================
REM  Instalador de Servico do Windows
REM  Pendencias Scheduler
REM ====================================

REM Verificar privilégios de administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Este script precisa ser executado como Administrador!
    echo Clique com botao direito e selecione "Executar como administrador"
    pause
    exit /b 1
)

echo ====================================
echo  Instalador de Servico
echo ====================================
echo.

set SERVICE_NAME=PendenciasScheduler
set SERVICE_DISPLAY=Pendencias Scheduler Service
set SERVICE_DESC=Servico automatico para execucao agendada de consultas de pendencias
set CURRENT_DIR=%~dp0
set EXE_PATH=%CURRENT_DIR%PendenciasScheduler.exe

REM Verificar se o executável existe
if not exist "%EXE_PATH%" (
    echo Erro: PendenciasScheduler.exe nao encontrado em:
    echo %EXE_PATH%
    echo.
    echo Execute build.bat primeiro para gerar o executavel.
    pause
    exit /b 1
)

REM Verificar se o NSSM está disponível
where nssm >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo NSSM (Non-Sucking Service Manager) nao encontrado!
    echo.
    echo Para instalar o servico, voce precisa:
    echo   1. Baixar NSSM de: https://nssm.cc/download
    echo   2. Extrair e adicionar ao PATH do Windows
    echo   3. Ou colocar nssm.exe na mesma pasta deste script
    echo.
    echo Alternativa: Use o Agendador de Tarefas do Windows
    echo   - Execute: taskschd.msc
    echo   - Crie uma nova tarefa para executar: %EXE_PATH%
    pause
    exit /b 1
)

echo Instalando servico...
nssm install %SERVICE_NAME% "%EXE_PATH%"
nssm set %SERVICE_NAME% DisplayName "%SERVICE_DISPLAY%"
nssm set %SERVICE_NAME% Description "%SERVICE_DESC%"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppDirectory "%CURRENT_DIR%"

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo  Servico instalado com sucesso!
    echo ====================================
    echo.
    echo Nome do servico: %SERVICE_NAME%
    echo.
    echo Para iniciar o servico:
    echo   net start %SERVICE_NAME%
    echo.
    echo Para parar o servico:
    echo   net stop %SERVICE_NAME%
    echo.
    echo Para remover o servico:
    echo   sc delete %SERVICE_NAME%
    echo.
) else (
    echo.
    echo ====================================
    echo  Erro ao instalar o servico!
    echo ====================================
    echo.
)

pause
