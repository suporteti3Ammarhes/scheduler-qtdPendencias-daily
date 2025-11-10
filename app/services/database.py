
import pyodbc
import pandas as pd
import logging
from typing import Optional, List, Any, Dict
from contextlib import contextmanager

# Import com fallback
try:
    from config.settings import DATABASE_CONFIG
except ImportError:
    DATABASE_CONFIG = {
        'server': 'agendatenicabr.database.windows.net',
        'database': 'agenda',
        'username': 'agenda',
        'password': 'kFN2IEqOupim0KieNDDmbqD',
        'driver': '{ODBC Driver 17 for SQL Server}',
        'port': 1433,
        'timeout': 30
    }


class DatabaseService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._connection = None
    
    def _get_connection_string(self) -> str:
        return (
            f"DRIVER={DATABASE_CONFIG['driver']};"
            f"SERVER={DATABASE_CONFIG['server']},{DATABASE_CONFIG['port']};"
            f"DATABASE={DATABASE_CONFIG['database']};"
            f"UID={DATABASE_CONFIG['username']};"
            f"PWD={DATABASE_CONFIG['password']};"
            f"Encrypt=yes;TrustServerCertificate=no;Connection Timeout={DATABASE_CONFIG['timeout']};"
        )
    
    @contextmanager
    def get_connection(self):
        connection = None
        try:
            self.logger.info("Connecting to database...")
            connection = pyodbc.connect(self._get_connection_string())
            self.logger.info("Database connection established successfully")
            yield connection
        except Exception as e:
            self.logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()
                self.logger.info("Database connection closed")
    
    def test_connection(self) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 as test")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, query: str) -> Optional[List[Dict[str, Any]]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                
                # Obter nomes das colunas
                columns = [column[0] for column in cursor.description]
                
                # Buscar todos os resultados
                rows = cursor.fetchall()
                
                # Converter para lista de dicionários
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                self.logger.info(f"Query executed successfully. {len(results)} records found")
                return results
                
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return None
    
    def execute_query_to_dataframe(self, query: str) -> Optional[pd.DataFrame]:
        try:
            with self.get_connection() as conn:
                df = pd.read_sql(query, conn)
                self.logger.info(f"Query executed successfully. DataFrame created with {len(df)} records")
                return df
        except Exception as e:
            self.logger.error(f"Error executing DataFrame query: {e}")
            return None