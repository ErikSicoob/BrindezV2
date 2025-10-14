# -*- coding: utf-8 -*-
"""
Gerenciador de Conexão com Banco de Dados
"""
import sqlite3
import os
from pathlib import Path
from config.settings import DB_PATH
from utils.logger import info, error, warning, debug


class DatabaseConnection:
    """Gerenciador de conexão com SQLite"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._connection is None:
            self._initialize_database()
    
    def _initialize_database(self):
        """Inicializa o banco de dados"""
        try:
            info("Inicializando banco de dados...")
            
            # Obter caminho absoluto do banco
            if os.path.isabs(DB_PATH):
                db_path = DB_PATH
            else:
                # Caminho relativo à raiz do projeto
                project_root = Path(__file__).parent.parent
                db_path = os.path.join(project_root, DB_PATH)
            
            # Criar backup automático se o banco já existir
            if os.path.exists(db_path):
                try:
                    from utils.backup_manager import backup_manager
                    backup_path = backup_manager.auto_backup_if_needed()
                    if backup_path:
                        info(f"Backup automático criado: {os.path.basename(backup_path)}")
                except Exception as e:
                    warning(f"Erro no backup automático: {e}")
            
            debug(f"Caminho do banco: {db_path}")
            
            # Criar diretório se não existir
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                info(f"Diretório criado: {db_dir}")
            
            # Conectar ao banco
            self._connection = sqlite3.connect(db_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            info("Conexão estabelecida com sucesso")
            
            # Habilitar foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
            debug("Foreign keys habilitadas")
            
            # Executar schema
            self._execute_schema()
            
            # Executar dados iniciais
            self._execute_initial_data()
            
            info(f"Banco de dados inicializado: {db_path}")
        except Exception as e:
            error(f"Erro ao inicializar banco de dados: {e}")
            raise
    
    def _execute_schema(self):
        """Executa o schema SQL"""
        schema_path = Path(__file__).parent / "schema.sql"
        
        if schema_path.exists():
            debug(f"Executando schema: {schema_path}")
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            cursor = self._connection.cursor()
            
            # Executar comandos individualmente para manter foreign keys
            commands = [cmd.strip() for cmd in schema_sql.split(';') if cmd.strip()]
            
            for command in commands:
                if command:
                    cursor.execute(command)
            
            self._connection.commit()
            
            # Reabilitar foreign keys após executar schema
            self._connection.execute("PRAGMA foreign_keys = ON")
            self._connection.commit()
            
            info("Schema do banco de dados criado/atualizado")
        else:
            warning("Arquivo schema.sql não encontrado")
    
    def _execute_initial_data(self):
        """Executa dados iniciais se necessário"""
        try:
            # Verificar se já existem dados
            cursor = self._connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM filiais")
            filiais_count = cursor.fetchone()[0]
            debug(f"Contagem de filiais no banco: {filiais_count}")
            
            if filiais_count == 0:
                # Executar dados iniciais
                initial_data_path = Path(__file__).parent / "initial_data.sql"
                
                if initial_data_path.exists():
                    debug(f"Executando dados iniciais: {initial_data_path}")
                    with open(initial_data_path, 'r', encoding='utf-8') as f:
                        initial_sql = f.read()
                    
                    # Remover comentários e dividir comandos
                    lines = initial_sql.split('\n')
                    clean_lines = []
                    for line in lines:
                        # Remover comentários
                        if '--' in line:
                            line = line[:line.index('--')]
                        line = line.strip()
                        if line:
                            clean_lines.append(line)
                    
                    clean_sql = ' '.join(clean_lines)
                    commands = [cmd.strip() for cmd in clean_sql.split(';') if cmd.strip()]
                    
                    for command in commands:
                        if command:
                            try:
                                cursor.execute(command)
                                debug(f"Comando executado: {command[:50]}...")
                            except Exception as cmd_error:
                                warning(f"Erro ao executar comando: {cmd_error}")
                                warning(f"Comando: {command[:100]}")
                    
                    self._connection.commit()
                    info("Dados iniciais inseridos")
                else:
                    warning("Arquivo initial_data.sql não encontrado")
            else:
                debug("Dados iniciais já existem, pulando inserção")
                
        except Exception as e:
            warning(f"Erro ao executar dados iniciais: {e}")
    
    def create_backup(self, reason="manual"):
        """Cria backup do banco de dados"""
        try:
            from utils.backup_manager import backup_manager
            return backup_manager.create_backup(reason)
        except Exception as e:
            error(f"Erro ao criar backup: {e}")
            return None
    
    def list_backups(self):
        """Lista backups disponíveis"""
        try:
            from utils.backup_manager import backup_manager
            return backup_manager.list_backups()
        except Exception as e:
            error(f"Erro ao listar backups: {e}")
            return []
    
    def restore_backup(self, backup_path):
        """Restaura backup específico"""
        try:
            from utils.backup_manager import backup_manager
            success = backup_manager.restore_backup(backup_path)
            if success:
                # Reconectar ao banco restaurado
                self._connection.close()
                self._connection = None
                self._initialize_database()
            return success
        except Exception as e:
            error(f"Erro ao restaurar backup: {e}")
            return False
    
    def get_connection(self):
        """Retorna a conexão ativa"""
        return self._connection
    
    def execute_query(self, query, params=None):
        """Executa uma query SELECT e retorna os resultados"""
        try:
            debug(f"Executando query: {query[:100]}...")
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            debug(f"Query retornou {len(results)} resultados")
            return results
        except Exception as e:
            error(f"Erro ao executar query: {e}")
            error(f"Query: {query}")
            error(f"Params: {params}")
            raise
    
    def execute_update(self, query, params=None):
        """Executa uma query INSERT/UPDATE/DELETE"""
        try:
            debug(f"Executando update: {query[:100]}...")
            cursor = self._connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self._connection.commit()
            lastrowid = cursor.lastrowid
            info(f"Update executado com sucesso (ID: {lastrowid})")
            return lastrowid
        except Exception as e:
            self._connection.rollback()
            error(f"Erro ao executar update: {e}")
            error(f"Query: {query}")
            error(f"Params: {params}")
            raise
    
    def execute_many(self, query, params_list):
        """Executa múltiplas queries"""
        cursor = self._connection.cursor()
        cursor.executemany(query, params_list)
        self._connection.commit()
        return cursor.rowcount
    
    def close(self):
        """Fecha a conexão"""
        if self._connection:
            self._connection.close()
            self._connection = None
            info("Conexão com banco de dados fechada")


# Instância global
db = DatabaseConnection()

# Updated: 2025-10-14 14:28:20
