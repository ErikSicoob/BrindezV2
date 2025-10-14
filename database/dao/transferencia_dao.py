# -*- coding: utf-8 -*-
"""
DAO para Transferências
"""
from database.connection import db


class TransferenciaDAO:
    """Data Access Object para Transferências"""
    
    @staticmethod
    def create(brinde_id, filial_origem_id, filial_destino_id, quantidade, usuario_id, justificativa):
        """Registra uma transferência"""
        query = """
            INSERT INTO transferencias (
                brinde_id, filial_origem_id, filial_destino_id,
                quantidade, usuario_id, justificativa
            ) VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            brinde_id, filial_origem_id, filial_destino_id,
            quantidade, usuario_id, justificativa
        )
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(filial_id=None, limit=100):
        """Retorna todas as transferências"""
        query = "SELECT * FROM vw_transferencias_completas"
        params = None
        
        if filial_id:
            query += " WHERE filial_origem_id = ? OR filial_destino_id = ?"
            params = (filial_id, filial_id)
        
        query += f" LIMIT {limit}"
        
        rows = db.execute_query(query, params)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_brinde(brinde_id, limit=50):
        """Retorna transferências de um brinde específico"""
        query = """
            SELECT * FROM vw_transferencias_completas
            WHERE brinde_id = ?
            LIMIT ?
        """
        rows = db.execute_query(query, (brinde_id, limit))
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_period(data_inicio, data_fim, filial_id=None):
        """Retorna transferências por período"""
        query = """
            SELECT * FROM vw_transferencias_completas
            WHERE DATE(data_transferencia) BETWEEN DATE(?) AND DATE(?)
        """
        params = [data_inicio, data_fim]
        
        if filial_id:
            query += " AND (filial_origem_id = ? OR filial_destino_id = ?)"
            params.extend([filial_id, filial_id])
        
        rows = db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

# Updated: 2025-10-14 14:28:20
