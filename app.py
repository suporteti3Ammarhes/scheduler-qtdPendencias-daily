import schedule
import time
import sys
import os
from pathlib import Path
from datetime import datetime
import threading
import logging

sys.path.append(str(Path(__file__).parent.parent))

from app.services.pendencias import PendenciasService
from app.services.database import DatabaseService

class PendenciasScheduler:
    def __init__(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scheduler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.database_service = DatabaseService()
        self.pendencias_service = PendenciasService()
        self.running = False
        
    def executar_consultas_agendadas(self):
        try:
            self.logger.info("Iniciando execução agendada de consultas de pendências")
            
            if not self.database_service.test_connection():
                self.logger.error("Teste de conexão com banco de dados falhou - abortando execução")
                return False
            
            self.logger.info("Conexão com banco de dados verificada - prosseguindo com execução das consultas")
            
            resumo = self.pendencias_service.executar_todas_consultas()
            
            if resumo:
                self.logger.info(f"Execução concluída com sucesso: {resumo.consultas_executadas} consultas executadas")
                self.logger.info(f"Total de pendências encontradas: {resumo.total_pendencias_encontradas}")
                self.logger.info(f"Taxa de sucesso: {resumo.taxa_sucesso:.1f}%")
                return True
            else:
                self.logger.error("Execução falhou - nenhum resultado retornado")
                return False
                
        except KeyboardInterrupt:
            self.logger.info("Execução interrompida pelo usuário")
            return False
        except Exception as e:
            self.logger.error(f"Erro na execução agendada: {str(e)}")
            import traceback
            self.logger.error(f"Rastreamento completo: {traceback.format_exc()}")
            return False
    
    def iniciar_scheduler(self):
        self.logger.info("Inicializando agendador para execução diária às 19:39")
        
        schedule.clear()
        schedule.every().day.at("20:10").do(self.executar_consultas_agendadas)
        
        self.running = True
        self.logger.info("Agendador iniciado com sucesso")
        
        last_log_time = time.time()
        
        while self.running:
            try:
                schedule.run_pending()
                
                current_time = time.time()
                if current_time - last_log_time >= 300:  
                    next_run = schedule.next_run()
                    if next_run:
                        time_until_next = next_run - datetime.now()
                        self.logger.info(f"Agendador em execução - próxima execução em {time_until_next}")
                    else:
                        self.logger.info("Agendador em execução - nenhum trabalho agendado")
                    last_log_time = current_time
                
                time.sleep(60)
                
            except KeyboardInterrupt:
                self.logger.info("Agendador interrompido pelo usuário")
                break
            except Exception as e:
                self.logger.error(f"Erro no loop do agendador: {e}")
                time.sleep(60)
    
    def parar_scheduler(self):
        self.running = False
        self.logger.info("Agendador interrompido")
    
    def executar_agora(self):
        self.logger.info("Executando consultas imediatamente")
        success = self.executar_consultas_agendadas()
        if success:
            self.logger.info("Execução imediata concluída com sucesso")
        else:
            self.logger.error("Execução imediata falhou")
        return success
    
    def proximo_agendamento(self):
        jobs = schedule.get_jobs()
        if jobs:
            next_run = min(job.next_run for job in jobs)
            self.logger.info(f"Próxima execução agendada para: {next_run}")
            return next_run
        return None

def main():
    try:
        Path('logs').mkdir(exist_ok=True)
        
        scheduler = PendenciasScheduler()
        
        scheduler.executar_agora()
        
        scheduler.iniciar_scheduler()
        
    except Exception as e:
        print(f"Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()