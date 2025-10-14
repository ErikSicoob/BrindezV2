# -*- coding: utf-8 -*-
"""
DAO para Movimentações
"""
from database.connection import db


class MovimentacaoDAO:
    """Data Access Object para Movimentações"""
    
    @staticmethod
    def create_entrada(brinde_id, quantidade, valor_unitario, usuario_id, justificativa=None):
        """Registra uma entrada de estoque"""
        query = """
            INSERT INTO movimentacoes (
                brinde_id, tipo, quantidade, valor_unitario, usuario_id, justificativa
            ) VALUES (?, 'ENTRADA', ?, ?, ?, ?)
        """
        params = (brinde_id, quantidade, valor_unitario, usuario_id, justificativa)
        return db.execute_update(query, params)
    
    @staticmethod
    def create_saida(brinde_id, quantidade, usuario_id, justificativa):
        """Registra uma saída de estoque"""
        query = """
            INSERT INTO movimentacoes (
                brinde_id, tipo, quantidade, usuario_id, justificativa
            ) VALUES (?, 'SAIDA', ?, ?, ?)
        """
        params = (brinde_id, quantidade, usuario_id, justificativa)
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(filial_id=None, limit=100):
        """Retorna todas as movimentações"""
        query = "SELECT * FROM vw_movimentacoes_completas"
        params = None
        
        if filial_id:
            query += " WHERE filial_id = ?"
            params = (filial_id,)
        
        query += f" LIMIT {limit}"
        
        rows = db.execute_query(query, params)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_brinde(brinde_id, limit=50):
        """Retorna movimentações de um brinde específico"""
        query = """
            SELECT * FROM vw_movimentacoes_completas
            WHERE brinde_id = ?
            LIMIT ?
        """
        rows = db.execute_query(query, (brinde_id, limit))
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_period(data_inicio, data_fim, filial_id=None):
        """Retorna movimentações por período"""
        query = """
            SELECT * FROM vw_movimentacoes_completas
            WHERE DATE(data_movimentacao) BETWEEN DATE(?) AND DATE(?)
        """
        params = [data_inicio, data_fim]
        
        if filial_id:
            query += " AND filial_id = ?"
            params.append(filial_id)
        
        rows = db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

# Updated: 2025-10-14 14:28:20
