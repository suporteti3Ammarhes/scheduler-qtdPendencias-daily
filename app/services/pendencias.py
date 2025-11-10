import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.models.pendencia import Pendencia, ResultadoExecucao, ResumoExecucao
from app.services.database import DatabaseService

try:
    from config.settings import MAIN_QUERY, APP_CONFIG
except ImportError:
    MAIN_QUERY = "SELECT id, id_pendencia, consulta_pendencia, id_grupo, nome_pendencia, dt_criacao, dt_modificacao FROM amm_consulta_pendencias ORDER BY id"
    APP_CONFIG = {'output_dir': 'output'}


class PendenciasService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_service = DatabaseService()
        self.output_dir = Path(APP_CONFIG['output_dir'])
        self.output_dir.mkdir(exist_ok=True)
        self.user_id = APP_CONFIG['user_id']
    
    def _obter_usuarios_responsaveis(self, conn, id_pendencia: int) -> List[Dict[str, Any]]:
        try:
            cursor = conn.cursor()
            
            query_usuarios = """
            SELECT uxp.idUsu, u.nome
            FROM amm_usuarios_x_pendencias uxp
            JOIN amm_usuarios u ON u.id = uxp.idUsu
            WHERE uxp.idPendencia = ?
            """
            
            cursor.execute(query_usuarios, (id_pendencia,))
            resultados = cursor.fetchall()
            
            usuarios = []
            for row in resultados:
                usuarios.append({
                    'id_usuario': row[0],
                    'nome_usuario': row[1]
                })
            
            self.logger.debug(f"Found {len(usuarios)} responsible users for pendência {id_pendencia}")
            return usuarios
            
        except Exception as e:
            self.logger.error(f"Error getting responsible users for pendência {id_pendencia}: {str(e)}")
            return []
    
    def _inserir_historico_pendencia(self, conn, id_pendencia: int, quantidade: int, id_usuario: int = None) -> bool:
        try:
            agora = datetime.now()
            data_atual = agora.strftime('%Y-%m-%d')
            hora_atual = agora.strftime('%H:%M:%S')
            
            cursor = conn.cursor()
            
            # Obter os usuários responsáveis por esta pendência
            usuarios_responsaveis = self._obter_usuarios_responsaveis(conn, id_pendencia)
            
            if not usuarios_responsaveis:
                # Se não há usuários responsáveis, usar o usuário padrão
                id_usuario_para_usar = id_usuario if id_usuario is not None else self.user_id
                nome_usuario = "Sistema"
                self.logger.warning(f"No responsible users found for pendência {id_pendencia}, using default user {id_usuario_para_usar}")
            else:
                # Usar apenas o primeiro usuário responsável
                primeiro_usuario = usuarios_responsaveis[0]
                id_usuario_para_usar = primeiro_usuario['id_usuario']
                nome_usuario = primeiro_usuario['nome_usuario']
                
                # Log informativo sobre todos os usuários encontrados
                if len(usuarios_responsaveis) > 1:
                    outros_usuarios = [f"{u['nome_usuario']} (ID: {u['id_usuario']})" for u in usuarios_responsaveis[1:]]
                    self.logger.info(f"Pendência {id_pendencia} has {len(usuarios_responsaveis)} responsible users. Using first: {nome_usuario} (ID: {id_usuario_para_usar}). Others: {', '.join(outros_usuarios)}")
                else:
                    self.logger.debug(f"Pendência {id_pendencia} - Using responsible user: {nome_usuario} (ID: {id_usuario_para_usar})")
            
            # Verificar se já existe registro para esta pendência hoje
            query_verificar = """
            SELECT COUNT(*) as total 
            FROM amm_histPendencias 
            WHERE idPendencia = ? AND data = ?
            """
            
            cursor.execute(query_verificar, (id_pendencia, data_atual))
            resultado = cursor.fetchone()
            existe_registro = resultado[0] > 0
            
            if existe_registro:
                query_update = """
                UPDATE amm_histPendencias 
                SET hora = ?, idUsuario = ?, qtd = ?, idGestora = 919, usoSistema = 1, responsabilidade = ''
                WHERE idPendencia = ? AND data = ?
                """
                cursor.execute(query_update, (hora_atual, id_usuario_para_usar, quantidade, id_pendencia, data_atual))
                self.logger.debug(f"Updated history for pendência {id_pendencia} with user {nome_usuario} (ID: {id_usuario_para_usar})")
            else:
                query_insert = """
                INSERT INTO amm_histPendencias 
                (idPendencia, data, hora, idUsuario, qtd, idGestora, usoSistema, responsabilidade)
                VALUES (?, ?, ?, ?, ?, 919, 1, '')
                """
                cursor.execute(query_insert, (id_pendencia, data_atual, hora_atual, id_usuario_para_usar, quantidade))
                self.logger.debug(f"Inserted history for pendência {id_pendencia} with user {nome_usuario} (ID: {id_usuario_para_usar})")
            
            conn.commit()
            self.logger.info(f"History updated for pendência {id_pendencia} - User: {nome_usuario} (ID: {id_usuario_para_usar}) - Quantity: {quantidade}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert/update history for pendência {id_pendencia}: {e}")
            return False
    
    def extrair_pendencias(self) -> Optional[List[Pendencia]]:
        results = self.db_service.execute_query(MAIN_QUERY)
        if not results:
            self.logger.error("Failed to extract pendências from database")
            return None
        
        pendencias = []
        for row in results:
            pendencia = Pendencia(
                id=row['id'],
                id_pendencia=row['id_pendencia'],
                consulta_pendencia=row['consulta_pendencia'],
                id_grupo=row.get('id_grupo'),
                nome_pendencia=row.get('nome_pendencia'),
                dt_criacao=row.get('dt_criacao'),
                dt_modificacao=row.get('dt_modificacao'),
                exibe_contagem=row.get('exibe_contagem')
            )
            pendencias.append(pendencia)
        
        return pendencias
    
    def executar_todas_consultas(self) -> Optional[ResumoExecucao]:
        self.logger.info("Starting execution of all pendência queries")
        self.logger.info("=" * 60)
        
        # Extrair pendências
        pendencias = self.extrair_pendencias()
        if not pendencias:
            return None
        
        self.logger.info(f" Total de consultas para executar: {len(pendencias)}")
        self.logger.info("-" * 60)
        
        resultados = []
        consultas_executadas = 0
        consultas_com_erro = 0
        
        # Executar com conexão única
        try:
            self.logger.info("Opening database connection for batch execution...")
            with self.db_service.get_connection() as conn:
                self.logger.info("Database connection opened successfully - starting query execution")
                
                for i, pendencia in enumerate(pendencias, 1):
                    self.logger.info(f"Executing query {i}/{len(pendencias)}: {pendencia.nome_pendencia}")
                    
                    try:
                        resultado = self._executar_consulta_individual(
                            conn, pendencia, i, len(pendencias)
                        )
                        resultados.append(resultado)
                        
                        if resultado.status == 'sucesso':
                            consultas_executadas += 1
                            self.logger.info(f"Query {i} completed successfully - {resultado.quantidade} records")
                        else:
                            consultas_com_erro += 1
                            self.logger.warning(f"Query {i} failed: {resultado.erro}")
                            
                        # Progress log every 10 queries
                        if i % 10 == 0:
                            self.logger.info(f"Progress: {i}/{len(pendencias)} queries processed ({(i/len(pendencias)*100):.1f}%)")
                            
                    except KeyboardInterrupt:
                        self.logger.info(f"Execution interrupted by user at query {i}")
                        break
                    except Exception as e:
                        self.logger.error(f"Error executing query {i}: {str(e)}")
                        consultas_com_erro += 1
                        
                self.logger.info("Batch execution completed - closing database connection")
        
        except Exception as e:
            self.logger.error(f"Critical execution error: {e}")
            import traceback
            self.logger.error(f"Full traceback: {traceback.format_exc()}")
            return None
        
        # Criar resumo
        resumo = self._criar_resumo_execucao(
            resultados, len(pendencias), consultas_executadas, consultas_com_erro
        )
        
        # Salvar resultados
        self._salvar_resultados(resumo)
        
        return resumo
    
    def _executar_consulta_individual(
        self, 
        conn, 
        pendencia: Pendencia, 
        index: int, 
        total: int
    ) -> ResultadoExecucao:
        nome_display = pendencia.nome_pendencia or f"Pendência {pendencia.id_pendencia}"
        
        try:
            self.logger.debug(f"Creating cursor for {nome_display}")
            cursor = conn.cursor()
            
            self.logger.debug(f"Executing SQL for {nome_display}: {pendencia.consulta_pendencia[:100]}...")
            cursor.execute(pendencia.consulta_pendencia)
            
            self.logger.debug(f"Fetching results for {nome_display}")
            row = cursor.fetchone()
            
            if row and len(row) > 0:
                quantidade = int(row[0]) if row[0] is not None else 0
                self.logger.debug(f"Query result for {nome_display}: {quantidade} records")
                
                self.logger.debug(f"Inserting history for {nome_display}")
                self._inserir_historico_pendencia(conn, pendencia.id_pendencia, quantidade)
                
                return ResultadoExecucao(
                    id=pendencia.id,
                    id_pendencia=pendencia.id_pendencia,
                    nome_pendencia=pendencia.nome_pendencia,
                    id_grupo=pendencia.id_grupo,
                    quantidade=quantidade,
                    status='sucesso',
                    exibe_contagem=pendencia.exibe_contagem,
                    consulta_preview=pendencia.consulta_pendencia[:100] + "..." if len(pendencia.consulta_pendencia) > 100 else pendencia.consulta_pendencia
                )
            else:
                self.logger.warning(f"No results for query: {nome_display}")
                
                self._inserir_historico_pendencia(conn, pendencia.id_pendencia, 0)
                
                return ResultadoExecucao(
                    id=pendencia.id,
                    id_pendencia=pendencia.id_pendencia,
                    nome_pendencia=pendencia.nome_pendencia,
                    id_grupo=pendencia.id_grupo,
                    quantidade=0,
                    status='sucesso',
                    exibe_contagem=pendencia.exibe_contagem
                )
                
        except Exception as e:
            self.logger.error(f"Error executing query for {nome_display}: {str(e)}")
            return ResultadoExecucao(
                id=pendencia.id,
                id_pendencia=pendencia.id_pendencia,
                nome_pendencia=pendencia.nome_pendencia,
                id_grupo=pendencia.id_grupo,
                quantidade=None,
                status='erro',
                exibe_contagem=pendencia.exibe_contagem,
                erro=str(e),
                consulta_preview=pendencia.consulta_pendencia[:100] + "..." if len(pendencia.consulta_pendencia) > 100 else pendencia.consulta_pendencia
            )
    
    def _criar_resumo_execucao(
        self, 
        resultados: List[ResultadoExecucao], 
        total: int, 
        executadas: int, 
        erros: int
    ) -> ResumoExecucao:
        # Calcular estatísticas
        resultados_com_dados = [r for r in resultados if r.status == 'sucesso' and r.quantidade and r.quantidade > 0]
        total_pendencias = sum(r.quantidade for r in resultados_com_dados)
        
        # Top 5 pendências
        top_pendencias = sorted(resultados_com_dados, key=lambda x: x.quantidade, reverse=True)[:5]
        top_list = []
        for i, pend in enumerate(top_pendencias, 1):
            nome_display = pend.nome_pendencia or f"Pendência {pend.id_pendencia}"
            top_list.append({
                'posicao': i,
                'id': pend.id,
                'nome': nome_display,
                'quantidade': pend.quantidade
            })
        
        return ResumoExecucao(
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            total_consultas=total,
            consultas_executadas=executadas,
            consultas_com_erro=erros,
            total_pendencias_encontradas=total_pendencias,
            resultados=resultados,
            top_pendencias=top_list
        )
    
    def _salvar_resultados(self, resumo: ResumoExecucao) -> None:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"resultados_execucao_pendencias_{timestamp}.json"
            filepath = self.output_dir / filename
            
            # Converter resultados para dict
            data = {
                'timestamp': resumo.timestamp,
                'total_consultas': resumo.total_consultas,
                'consultas_executadas': resumo.consultas_executadas,
                'consultas_com_erro': resumo.consultas_com_erro,
                'total_pendencias_encontradas': resumo.total_pendencias_encontradas,
                'taxa_sucesso': resumo.taxa_sucesso,
                'top_pendencias': resumo.top_pendencias,
                'resultados': {
                    str(r.id): {
                        'id': r.id,
                        'id_pendencia': r.id_pendencia,
                        'nome_pendencia': r.nome_pendencia,
                        'id_grupo': r.id_grupo,
                        'total_registros': r.quantidade,
                        'exibe_contagem': r.exibe_contagem,
                        'status': r.status,
                        'erro': r.erro,
                        'consulta_preview': r.consulta_preview
                    }
                    for r in resumo.resultados
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
            
        except Exception as e:
            self.logger.error(f"Error saving results: {e}")
    
    def imprimir_resumo_final(self, resumo: ResumoExecucao) -> None:
        print("\n" + "=" * 60)
        print("EXECUTION SUMMARY")
        print("=" * 60)
        print(f"Successful queries: {resumo.consultas_executadas}")
        print(f"Failed queries: {resumo.consultas_com_erro}")
        print(f"Success rate: {resumo.taxa_sucesso:.1f}%")
        print(f"Total pendências found: {resumo.total_pendencias_encontradas}")
        
        if resumo.top_pendencias:
            print(f"\nTOP 5 PENDÊNCIAS COM MAIORES RESULTADOS:")
            for top in resumo.top_pendencias:
                print(f"   {top['posicao']}. ID {top['id']} - {top['nome']}: {top['quantidade']} items")
        
        print("Reports saved successfully!")