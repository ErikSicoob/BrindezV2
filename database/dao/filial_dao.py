# -*- coding: utf-8 -*-
"""
DAO para Filiais
"""
from database.connection import db


class FilialDAO:
    """Data Access Object para Filiais"""
    
    @staticmethod
    def create(data):
        """Cria uma nova filial"""
        query = """
            INSERT INTO filiais (
                numero, nome, cidade, estado, endereco, 
                telefone, email, responsavel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('numero'),
            data.get('nome'),
            data.get('cidade'),
            data.get('estado'),
            data.get('endereco'),
            data.get('telefone'),
            data.get('email'),
            data.get('responsavel')
        )
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(ativo_apenas=True):
        """Retorna todas as filiais"""
        query = "SELECT * FROM filiais"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY numero"
        
        rows = db.execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(filial_id):
        """Retorna filial por ID"""
        query = "SELECT * FROM filiais WHERE id = ?"
        rows = db.execute_query(query, (filial_id,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def update(filial_id, data):
        """Atualiza uma filial"""
        query = """
            UPDATE filiais SET
                numero = ?, nome = ?, cidade = ?, estado = ?,
                endereco = ?, telefone = ?, email = ?, responsavel = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            data.get('numero'),
            data.get('nome'),
            data.get('cidade'),
            data.get('estado'),
            data.get('endereco'),
            data.get('telefone'),
            data.get('email'),
            data.get('responsavel'),
            filial_id
        )
        db.execute_update(query, params)
        return True
    
    @staticmethod
    def delete(filial_id):
        """Desativa uma filial"""
        query = "UPDATE filiais SET ativo = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (filial_id,))
        return True
    
    @staticmethod
    def activate(filial_id):
        """Ativa uma filial"""
        query = "UPDATE filiais SET ativo = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (filial_id,))
        return True
    
    @staticmethod
    def get_matriz():
        """Retorna a filial matriz"""
        query = "SELECT * FROM filiais WHERE is_matriz = 1 LIMIT 1"
        rows = db.execute_query(query)
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def set_matriz(filial_id):
        """Define uma filial como matriz"""
        # Remove matriz de todas as filiais
        db.execute_update("UPDATE filiais SET is_matriz = 0")
        # Define a nova matriz
        query = "UPDATE filiais SET is_matriz = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (filial_id,))
        return True
    
    @staticmethod
    def count_active():
        """Conta filiais ativas"""
        query = "SELECT COUNT(*) as count FROM filiais WHERE ativo = 1"
        result = db.execute_query(query)
        return result[0]['count'] if result else 0
    
    @staticmethod
    def is_matriz(filial_id):
        """Verifica se a filial é matriz"""
        query = "SELECT is_matriz FROM filiais WHERE id = ?"
        result = db.execute_query(query, (filial_id,))
        return result[0]['is_matriz'] == 1 if result else False
    
    @staticmethod
    def can_delete(filial_id):
        """Verifica se a filial pode ser excluída"""
        # Não pode excluir se for a única filial ativa
        total_ativas = FilialDAO.count_active()
        filial = FilialDAO.get_by_id(filial_id)
        
        if filial and filial['ativo'] and total_ativas <= 1:
            return False, "Não é possível excluir a única filial ativa do sistema!"
        
        # Verificar se há usuários ou brindes
        check_users = "SELECT COUNT(*) as count FROM usuarios WHERE filial_id = ?"
        result_users = db.execute_query(check_users, (filial_id,))
        
        check_brindes = "SELECT COUNT(*) as count FROM brindes WHERE filial_id = ?"
        result_brindes = db.execute_query(check_brindes, (filial_id,))
        
        if result_users[0]['count'] > 0 or result_brindes[0]['count'] > 0:
            return False, f"Não é possível excluir!\n\nUsuários: {result_users[0]['count']}\nBrindes: {result_brindes[0]['count']}\n\nDesative a filial ao invés de excluir."
        
        return True, ""

# Updated: 2025-10-14 14:28:20
