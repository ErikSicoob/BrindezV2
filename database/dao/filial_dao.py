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
