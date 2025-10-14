# -*- coding: utf-8 -*-
"""
DAO para Fornecedores
"""
from database.connection import db
from datetime import datetime


class FornecedorDAO:
    """Data Access Object para Fornecedores"""
    
    @staticmethod
    def create(data):
        """Cria um novo fornecedor"""
        query = """
            INSERT INTO fornecedores (
                nome, cnpj, contato, telefone, email, 
                endereco, cidade, estado, cep, observacoes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('nome'),
            data.get('cnpj'),
            data.get('contato'),
            data.get('telefone'),
            data.get('email'),
            data.get('endereco'),
            data.get('cidade'),
            data.get('estado'),
            data.get('cep'),
            data.get('observacoes')
        )
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(ativo_apenas=True):
        """Retorna todos os fornecedores"""
        query = "SELECT * FROM fornecedores"
        if ativo_apenas:
            query += " WHERE ativo = 1"
        query += " ORDER BY nome"
        
        rows = db.execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(fornecedor_id):
        """Retorna fornecedor por ID"""
        query = "SELECT * FROM fornecedores WHERE id = ?"
        rows = db.execute_query(query, (fornecedor_id,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def update(fornecedor_id, data):
        """Atualiza um fornecedor"""
        query = """
            UPDATE fornecedores SET
                nome = ?, cnpj = ?, contato = ?, telefone = ?,
                email = ?, endereco = ?, cidade = ?, estado = ?,
                cep = ?, observacoes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            data.get('nome'),
            data.get('cnpj'),
            data.get('contato'),
            data.get('telefone'),
            data.get('email'),
            data.get('endereco'),
            data.get('cidade'),
            data.get('estado'),
            data.get('cep'),
            data.get('observacoes'),
            fornecedor_id
        )
        db.execute_update(query, params)
        return True
    
    @staticmethod
    def delete(fornecedor_id):
        """Desativa um fornecedor"""
        query = "UPDATE fornecedores SET ativo = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (fornecedor_id,))
        return True
    
    @staticmethod
    def activate(fornecedor_id):
        """Ativa um fornecedor"""
        query = "UPDATE fornecedores SET ativo = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (fornecedor_id,))
        return True
    
    @staticmethod
    def search(termo):
        """Busca fornecedores por nome ou CNPJ"""
        query = """
            SELECT * FROM fornecedores 
            WHERE (nome LIKE ? OR cnpj LIKE ?) AND ativo = 1
            ORDER BY nome
        """
        termo_busca = f"%{termo}%"
        rows = db.execute_query(query, (termo_busca, termo_busca))
        return [dict(row) for row in rows]
