# -*- coding: utf-8 -*-
"""
DAO para Unidades de Medida
"""
from database.connection import db


class UnidadeDAO:
    """Data Access Object para Unidades de Medida"""
    
    @staticmethod
    def create(data):
        """Cria uma nova unidade"""
        query = "INSERT INTO unidades_medida (codigo, nome, descricao) VALUES (?, ?, ?)"
        params = (data.get('codigo'), data.get('nome'), data.get('descricao'))
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(ativo_apenas=True):
        """Retorna todas as unidades"""
        query = "SELECT * FROM unidades_medida"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY codigo"
        
        rows = db.execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(unidade_id):
        """Retorna unidade por ID"""
        query = "SELECT * FROM unidades_medida WHERE id = ?"
        rows = db.execute_query(query, (unidade_id,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def update(unidade_id, data):
        """Atualiza uma unidade"""
        query = """
            UPDATE unidades_medida SET
                codigo = ?, nome = ?, descricao = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (data.get('codigo'), data.get('nome'), data.get('descricao'), unidade_id)
        db.execute_update(query, params)
        return True
    
    @staticmethod
    def delete(unidade_id):
        """Desativa uma unidade"""
        # Verificar se há brindes associados
        check_query = "SELECT COUNT(*) as count FROM brindes WHERE unidade_id = ?"
        result = db.execute_query(check_query, (unidade_id,))
        
        if result[0]['count'] > 0:
            return False  # Não pode excluir
        
        query = "UPDATE unidades_medida SET ativo = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (unidade_id,))
        return True
    
    @staticmethod
    def activate(unidade_id):
        """Ativa uma unidade"""
        query = "UPDATE unidades_medida SET ativo = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (unidade_id,))
        return True

# Updated: 2025-10-14 14:28:20
