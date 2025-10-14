# -*- coding: utf-8 -*-
"""
DAO para Categorias
"""
from database.connection import db


class CategoriaDAO:
    """Data Access Object para Categorias"""
    
    @staticmethod
    def create(data):
        """Cria uma nova categoria"""
        query = "INSERT INTO categorias (nome, descricao) VALUES (?, ?)"
        params = (data.get('nome'), data.get('descricao'))
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(ativo_apenas=True):
        """Retorna todas as categorias"""
        query = "SELECT * FROM categorias"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        
        rows = db.execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(categoria_id):
        """Retorna categoria por ID"""
        query = "SELECT * FROM categorias WHERE id = ?"
        rows = db.execute_query(query, (categoria_id,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def update(categoria_id, data):
        """Atualiza uma categoria"""
        query = """
            UPDATE categorias SET
                nome = ?, descricao = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (data.get('nome'), data.get('descricao'), categoria_id)
        db.execute_update(query, params)
        return True
    
    @staticmethod
    def delete(categoria_id):
        """Desativa uma categoria"""
        # Verificar se há brindes associados
        check_query = "SELECT COUNT(*) as count FROM brindes WHERE categoria_id = ?"
        result = db.execute_query(check_query, (categoria_id,))
        
        if result[0]['count'] > 0:
            return False  # Não pode excluir
        
        query = "UPDATE categorias SET ativo = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (categoria_id,))
        return True
    
    @staticmethod
    def activate(categoria_id):
        """Ativa uma categoria"""
        query = "UPDATE categorias SET ativo = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (categoria_id,))
        return True

# Updated: 2025-10-14 14:28:20
