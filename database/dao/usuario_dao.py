# -*- coding: utf-8 -*-
"""
DAO para Usuários
"""
from database.connection import db


class UsuarioDAO:
    """Data Access Object para Usuários"""
    
    @staticmethod
    def create(data):
        """Cria um novo usuário"""
        query = """
            INSERT INTO usuarios (nome, username, email, perfil, filial_id)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (
            data.get('nome'),
            data.get('username'),
            data.get('email'),
            data.get('perfil'),
            data.get('filial_id')
        )
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(ativo_apenas=True):
        """Retorna todos os usuários"""
        query = """
            SELECT u.*, f.nome as filial_nome
            FROM usuarios u
            INNER JOIN filiais f ON u.filial_id = f.id
        """
        if ativo_apenas:
            query += " WHERE u.ativo = 1"
        query += " ORDER BY u.nome"
        
        rows = db.execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(usuario_id):
        """Retorna usuário por ID"""
        query = """
            SELECT u.*, f.nome as filial_nome
            FROM usuarios u
            INNER JOIN filiais f ON u.filial_id = f.id
            WHERE u.id = ?
        """
        rows = db.execute_query(query, (usuario_id,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def get_by_username(username):
        """Retorna usuário por username"""
        query = """
            SELECT u.*, f.nome as filial_nome
            FROM usuarios u
            INNER JOIN filiais f ON u.filial_id = f.id
            WHERE u.username = ? AND u.ativo = 1
        """
        rows = db.execute_query(query, (username,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def update(usuario_id, data):
        """Atualiza um usuário"""
        query = """
            UPDATE usuarios SET
                nome = ?, email = ?, perfil = ?, filial_id = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            data.get('nome'),
            data.get('email'),
            data.get('perfil'),
            data.get('filial_id'),
            usuario_id
        )
        db.execute_update(query, params)
        return True
    
    @staticmethod
    def delete(usuario_id):
        """Desativa um usuário"""
        query = "UPDATE usuarios SET ativo = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (usuario_id,))
        return True
    
    @staticmethod
    def activate(usuario_id):
        """Ativa um usuário"""
        query = "UPDATE usuarios SET ativo = 1, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        db.execute_update(query, (usuario_id,))
        return True
