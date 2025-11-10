"""
Configurações da aplicação
Arquivo de configuração centralizado para o sistema
"""
import os
from typing import Dict, Any

# Configurações do banco de dados
DATABASE_CONFIG: Dict[str, Any] = {
    'server': os.getenv('DB_SERVER', 'agendatenicabr.database.windows.net'),
    'database': os.getenv('DB_DATABASE', 'agenda'),
    'username': os.getenv('DB_USERNAME', 'agenda'),
    'password': os.getenv('DB_PASSWORD', 'kFN2IEqOupim0KieNDDmbqD'),
    'driver': os.getenv('DB_DRIVER', '{ODBC Driver 17 for SQL Server}'),
    'port': int(os.getenv('DB_PORT', '1433')),
    'timeout': int(os.getenv('DB_TIMEOUT', '30'))
}

# Configurações da aplicação
APP_CONFIG: Dict[str, Any] = {
    'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    'max_retries': int(os.getenv('MAX_RETRIES', '3')),
    'retry_delay': int(os.getenv('RETRY_DELAY', '5')),  # segundos
    'output_dir': os.getenv('OUTPUT_DIR', 'output'),
    'user_id': int(os.getenv('USER_ID', '1')),  # ID do usuário para histórico
    'version': '2.0.0'
}

# Query principal para buscar pendências
MAIN_QUERY: str = """
    SELECT 
        id,
        id_pendencia,
        consulta_pendencia,
        id_grupo,
        nome_pendencia,
        dt_criacao,
        dt_modificacao,
        exibe_contagem
    FROM amm_consulta_pendencias
    ORDER BY id
"""

# Query para testar conexão
TEST_QUERY: str = "SELECT 1 as test"