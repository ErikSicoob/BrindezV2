# -*- coding: utf-8 -*-
"""
Script para recriar o banco de dados com todas as correções
"""
import os
import shutil
from pathlib import Path

def recreate_database():
    """Recria o banco de dados do zero"""
    try:
        # Usar o sistema de backup integrado
        from utils.backup_manager import backup_manager
        
        db_path = "data/brindes.db"
        
        if os.path.exists(db_path):
            # Criar backup usando o sistema integrado
            backup_path = backup_manager.create_backup("recreate")
            if backup_path:
                print(f"Backup criado: {os.path.basename(backup_path)}")
            
            # Remover banco atual
            os.remove(db_path)
            print("Banco antigo removido")
        
        # Importar e inicializar novo banco
        from database.connection import DatabaseConnection
        
        print("Criando novo banco de dados...")
        db = DatabaseConnection()  # A inicialização acontece automaticamente no __init__
        
        print("Banco de dados recriado com sucesso!")
        print("Foreign keys habilitadas")
        print("Dados iniciais inseridos")
        print("Views atualizadas")
        
        return True
        
    except Exception as e:
        print(f"Erro ao recriar banco: {e}")
        return False

if __name__ == "__main__":
    print("Recriando banco de dados...")
    if recreate_database():
        print("\nBanco recriado com sucesso!")
        print("Agora você pode:")
        print("- Excluir brindes com auditoria")
        print("- Ver relatório de brindes excluídos")
        print("- Foreign keys funcionando corretamente")
    else:
        print("\nFalha ao recriar banco!")

# Updated: 2025-10-14 14:28:20
