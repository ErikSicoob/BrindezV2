# -*- coding: utf-8 -*-
"""
Script de Migração: Adiciona campo is_matriz na tabela filiais
"""
from database.connection import db


def migrate():
    """Adiciona campo is_matriz e define a filial mais antiga como matriz"""
    
    print("🔄 Iniciando migração: Adicionar campo is_matriz...")
    
    try:
        # 1. Adicionar coluna is_matriz
        print("  ➤ Adicionando coluna is_matriz...")
        alter_query = "ALTER TABLE filiais ADD COLUMN is_matriz BOOLEAN DEFAULT 0"
        db.execute_update(alter_query)
        print("  ✓ Coluna adicionada")
        
        # 2. Definir a filial mais antiga como matriz
        print("  ➤ Definindo filial mais antiga como matriz...")
        
        # Buscar a filial mais antiga (menor ID)
        query = "SELECT id, nome FROM filiais ORDER BY id ASC LIMIT 1"
        result = db.execute_query(query)
        
        if result:
            filial_matriz = result[0]
            update_query = "UPDATE filiais SET is_matriz = 1 WHERE id = ?"
            db.execute_update(update_query, (filial_matriz['id'],))
            print(f"  ✓ Filial '{filial_matriz['nome']}' (ID: {filial_matriz['id']}) definida como matriz")
        else:
            print("  ⚠ Nenhuma filial encontrada")
        
        print("\n✅ Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        if "duplicate column name" in error_msg.lower():
            print("  ⚠ Coluna is_matriz já existe. Pulando migração.")
            return True
        else:
            print(f"\n❌ Erro na migração: {e}")
            import traceback
            print(traceback.format_exc())
            return False


if __name__ == "__main__":
    migrate()

# Updated: 2025-10-14 14:28:20
