# Build e Execução do Scheduler - Guia Completo

## 📋 Pré-requisitos

Antes de construir o executável, certifique-se de ter:

1. **Python 3.8+** instalado
2. **PyInstaller** (será instalado automaticamente pelos scripts)
3. Todas as dependências instaladas:
   ```bash
   pip install -r requirements.txt
   ```

## 🔨 Como Construir o Executável

### Windows

Execute o arquivo `build.bat`:

```cmd
build.bat
```

Ou manualmente:

```cmd
pip install pyinstaller
pyinstaller PendenciasScheduler.spec
```

### Linux/Mac

Execute o arquivo `build.sh`:

```bash
chmod +x build.sh
./build.sh
```

## 🚀 Como Executar

### Modo 1: Executável Direto

**Windows:**
```cmd
dist\PendenciasScheduler.exe
```

**Linux/Mac:**
```bash
./dist/PendenciasScheduler
```

### Modo 2: Script de Execução

**Windows:**
```cmd
run.bat
```

### Modo 3: Python Direto (Desenvolvimento)

```bash
python app.py
```

## ⚙️ Configuração

### Arquivo .env

Certifique-se de ter um arquivo `.env` na mesma pasta do executável:

```env
# Configurações do Banco de Dados
DB_SERVER=seu_servidor
DB_DATABASE=seu_banco
DB_USERNAME=seu_usuario
DB_PASSWORD=sua_senha
DB_DRIVER={ODBC Driver 17 for SQL Server}

# Configurações do Scheduler
SCHEDULER_TIME=20:10
OUTPUT_DIR=output
```

## 🔧 Instalação como Serviço do Windows

Para executar o scheduler como um serviço do Windows (inicia automaticamente com o sistema):

### Opção 1: Usar NSSM (Recomendado)

1. Baixe o NSSM em: https://nssm.cc/download
2. Extraia e coloque `nssm.exe` na pasta do scheduler
3. Execute como Administrador:
   ```cmd
   install-service.bat
   ```

### Opção 2: Agendador de Tarefas do Windows

1. Abra o Agendador de Tarefas: `taskschd.msc`
2. Criar Tarefa Básica
3. Nome: "Pendencias Scheduler"
4. Gatilho: "Quando o computador iniciar"
5. Ação: "Iniciar um programa"
6. Programa: `C:\caminho\para\PendenciasScheduler.exe`
7. Marcar: "Executar com privilégios mais altos"

### Opção 3: Task Scheduler via PowerShell

```powershell
$action = New-ScheduledTaskAction -Execute "C:\caminho\para\PendenciasScheduler.exe"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "PendenciasScheduler" -Action $action -Trigger $trigger -Principal $principal -Description "Executa consultas de pendencias automaticamente"
```

## 📂 Estrutura de Arquivos Gerados

```
scheduler-app/
├── app.py                      # Código principal
├── build.bat                   # Script de build (Windows)
├── build.sh                    # Script de build (Linux/Mac)
├── run.bat                     # Script de execução (Windows)
├── install-service.bat         # Instalador de serviço (Windows)
├── PendenciasScheduler.spec    # Configuração PyInstaller
├── requirements.txt            # Dependências Python
├── .env                        # Configurações (não incluir no build)
├── build/                      # Arquivos temporários (ignorar)
└── dist/                       # Executável final
    └── PendenciasScheduler.exe # EXECUTÁVEL FINAL
```

## 📝 Logs

O scheduler gera logs em:
- **Console**: Saída padrão em tempo real
- **Arquivo**: `scheduler.log` na pasta do executável
- **Pasta logs/**: Logs detalhados das execuções

## 🐛 Solução de Problemas

### Erro: "PyInstaller não encontrado"
```bash
pip install pyinstaller
```

### Erro: "Arquivo .env não encontrado"
- Copie o arquivo `.env` para a pasta onde está o executável

### Erro: "Conexão com banco de dados falhou"
- Verifique as configurações no arquivo `.env`
- Teste a conexão manualmente:
  ```bash
  python -c "from app.services.database import DatabaseService; print(DatabaseService().test_connection())"
  ```

### Executável não inicia
- Execute via CMD/Terminal para ver mensagens de erro
- Verifique se todas as DLLs necessárias estão instaladas (ODBC Driver)

### Erro: "ODBC Driver não encontrado"
- Instale o Microsoft ODBC Driver 17 for SQL Server
- Download: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

## 🔄 Atualização

Para atualizar o executável após mudanças no código:

1. Faça as alterações necessárias no código
2. Execute novamente o build:
   ```cmd
   build.bat
   ```
3. Substitua o executável antigo pelo novo em `dist/`

## 📊 Monitoramento

### Verificar se está rodando (Windows)
```cmd
tasklist | findstr PendenciasScheduler
```

### Verificar logs em tempo real
```cmd
type scheduler.log
```

ou use:
```cmd
Get-Content scheduler.log -Wait -Tail 50
```

## 🛑 Parar o Scheduler

### Se executado manualmente
- Pressione `Ctrl+C` no terminal

### Se instalado como serviço
```cmd
net stop PendenciasScheduler
```

### Se via Agendador de Tarefas
```cmd
schtasks /end /tn "PendenciasScheduler"
```

## 📦 Distribuição

Para distribuir o executável:

1. Copie a pasta `dist/` com o executável
2. Inclua um arquivo `.env` de exemplo (sem senhas)
3. Inclua este README.md
4. Certifique-se de que o servidor alvo tenha:
   - Microsoft ODBC Driver 17 for SQL Server
   - Visual C++ Redistributable (geralmente já instalado)

## 🔐 Segurança

**IMPORTANTE:**
- ⚠️ Nunca inclua o arquivo `.env` com credenciais reais no executável
- ⚠️ O arquivo `.env` deve ser configurado separadamente em cada ambiente
- ✅ Use variáveis de ambiente do sistema em produção
- ✅ Mantenha backups das configurações

## 📞 Suporte

Em caso de problemas:
1. Verifique os logs em `scheduler.log`
2. Execute em modo debug: `python app.py`
3. Verifique a conectividade com o banco de dados
4. Confirme que todas as dependências estão instaladas
