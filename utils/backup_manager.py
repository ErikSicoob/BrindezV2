# -*- coding: utf-8 -*-
"""
Gerenciador de Backup do Banco de Dados
"""
import os
import shutil
import glob
from datetime import datetime
from pathlib import Path
from utils.logger import logger


class BackupManager:
    """Gerenciador de backups do banco de dados"""
    
    def __init__(self, db_path="data/brindes.db", backup_dir="data/backups"):
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.max_backups = 2  # Manter apenas 2 backups
        
        # Criar diretório de backup se não existir
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_backup(self, reason="manual"):
        """
        Cria um novo backup do banco de dados
        
        Args:
            reason (str): Motivo do backup (manual, auto, update, etc.)
        
        Returns:
            str: Caminho do backup criado ou None se falhou
        """
        try:
            if not os.path.exists(self.db_path):
                logger.warning(f"Banco de dados não encontrado: {self.db_path}")
                return None
            
            # Gerar nome do backup com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"brindes_backup_{timestamp}_{reason}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Criar backup
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"Backup criado: {backup_path}")
            
            # Limpar backups antigos
            self._cleanup_old_backups()
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Erro ao criar backup: {e}")
            return None
    
    def _cleanup_old_backups(self):
        """Remove backups antigos, mantendo apenas os mais recentes"""
        try:
            # Buscar todos os arquivos de backup
            backup_pattern = os.path.join(self.backup_dir, "brindes_backup_*.db")
            backup_files = glob.glob(backup_pattern)
            
            if len(backup_files) <= self.max_backups:
                return  # Não há backups suficientes para limpar
            
            # Ordenar por data de modificação (mais recente primeiro)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Manter apenas os mais recentes
            files_to_keep = backup_files[:self.max_backups]
            files_to_remove = backup_files[self.max_backups:]
            
            # Remover backups antigos
            for file_path in files_to_remove:
                try:
                    os.remove(file_path)
                    logger.info(f"Backup antigo removido: {os.path.basename(file_path)}")
                except Exception as e:
                    logger.error(f"Erro ao remover backup {file_path}: {e}")
            
            logger.info(f"Limpeza concluída. Mantidos {len(files_to_keep)} backups")
            
        except Exception as e:
            logger.error(f"Erro na limpeza de backups: {e}")
    
    def list_backups(self):
        """
        Lista todos os backups disponíveis
        
        Returns:
            list: Lista de dicionários com informações dos backups
        """
        try:
            backup_pattern = os.path.join(self.backup_dir, "brindes_backup_*.db")
            backup_files = glob.glob(backup_pattern)
            
            backups = []
            for file_path in backup_files:
                stat = os.stat(file_path)
                backup_info = {
                    "path": file_path,
                    "filename": os.path.basename(file_path),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_ctime),
                    "modified": datetime.fromtimestamp(stat.st_mtime)
                }
                backups.append(backup_info)
            
            # Ordenar por data de modificação (mais recente primeiro)
            backups.sort(key=lambda x: x["modified"], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Erro ao listar backups: {e}")
            return []
    
    def restore_backup(self, backup_path):
        """
        Restaura um backup específico
        
        Args:
            backup_path (str): Caminho do backup a ser restaurado
        
        Returns:
            bool: True se restaurado com sucesso, False caso contrário
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"Backup não encontrado: {backup_path}")
                return False
            
            # Criar backup do banco atual antes de restaurar
            current_backup = self.create_backup("pre_restore")
            if current_backup:
                logger.info(f"Backup atual criado antes da restauração: {current_backup}")
            
            # Restaurar backup
            shutil.copy2(backup_path, self.db_path)
            logger.info(f"Backup restaurado: {backup_path} -> {self.db_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def get_latest_backup(self):
        """
        Retorna o backup mais recente
        
        Returns:
            dict: Informações do backup mais recente ou None
        """
        backups = self.list_backups()
        return backups[0] if backups else None
    
    def auto_backup_if_needed(self, force=False):
        """
        Cria backup automático se necessário
        
        Args:
            force (bool): Forçar criação do backup
        
        Returns:
            str: Caminho do backup criado ou None
        """
        try:
            if force:
                return self.create_backup("forced")
            
            # Verificar se precisa de backup baseado na idade do último
            latest_backup = self.get_latest_backup()
            
            if not latest_backup:
                # Não há backups, criar um
                return self.create_backup("auto_first")
            
            # Verificar idade do último backup (criar se > 1 hora)
            age_hours = (datetime.now() - latest_backup["modified"]).total_seconds() / 3600
            
            if age_hours > 1:  # Mais de 1 hora
                return self.create_backup("auto_scheduled")
            
            logger.debug(f"Backup não necessário. Último backup: {age_hours:.1f}h atrás")
            return None
            
        except Exception as e:
            logger.error(f"Erro no backup automático: {e}")
            return None


# Instância global
backup_manager = BackupManager()

# Updated: 2025-10-14 14:28:20
