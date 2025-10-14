# -*- coding: utf-8 -*-
"""
DAO para Brindes Excluídos
"""
from database.connection import db
from utils.logger import logger


class BrindeExcluidoDAO:
    """Data Access Object para brindes excluídos"""
    
    @staticmethod
    def create_from_brinde(brinde_data, usuario_id, usuario_nome, motivo=None):
        """
        Cria um registro de brinde excluído a partir dos dados do brinde original
        """
        try:
            query = """
                INSERT INTO brindes_excluidos (
                    brinde_id_original, descricao, categoria_nome, unidade_codigo,
                    filial_nome, fornecedor_nome, quantidade, valor_unitario,
                    codigo_interno, observacoes, estoque_minimo, data_criacao,
                    usuario_exclusao_id, usuario_exclusao_nome, motivo_exclusao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            params = (
                brinde_data["id"],
                brinde_data["descricao"],
                brinde_data.get("categoria", ""),  # nome do campo na view
                brinde_data.get("unidade", ""),    # nome do campo na view
                brinde_data.get("filial", ""),     # nome do campo na view
                brinde_data.get("fornecedor", ""), # nome do campo na view
                brinde_data.get("quantidade", 0),
                brinde_data.get("valor_unitario", 0.0),
                brinde_data.get("codigo_interno"),
                brinde_data.get("observacoes"),
                brinde_data.get("estoque_minimo", 0),
                brinde_data.get("created_at"),
                usuario_id,
                usuario_nome,
                motivo
            )
            
            result = db.execute_update(query, params)
            logger.info(f"Brinde excluído registrado: ID {brinde_data['id']} por {usuario_nome}")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao registrar brinde excluído: {e}")
            raise
    
    @staticmethod
    def get_all(limit=100, offset=0):
        """Retorna todos os brindes excluídos com paginação"""
        try:
            query = """
                SELECT * FROM brindes_excluidos
                ORDER BY data_exclusao DESC
                LIMIT ? OFFSET ?
            """
            rows = db.execute_query(query, (limit, offset))
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro ao buscar brindes excluídos: {e}")
            return []
    
    @staticmethod
    def get_by_period(data_inicio, data_fim):
        """Retorna brindes excluídos por período"""
        try:
            query = """
                SELECT * FROM brindes_excluidos
                WHERE DATE(data_exclusao) BETWEEN ? AND ?
                ORDER BY data_exclusao DESC
            """
            rows = db.execute_query(query, (data_inicio, data_fim))
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro ao buscar brindes excluídos por período: {e}")
            return []
    
    @staticmethod
    def get_by_user(usuario_id):
        """Retorna brindes excluídos por usuário"""
        try:
            query = """
                SELECT * FROM brindes_excluidos
                WHERE usuario_exclusao_id = ?
                ORDER BY data_exclusao DESC
            """
            rows = db.execute_query(query, (usuario_id,))
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro ao buscar brindes excluídos por usuário: {e}")
            return []
    
    @staticmethod
    def count_total():
        """Retorna o total de brindes excluídos"""
        try:
            query = "SELECT COUNT(*) as total FROM brindes_excluidos"
            result = db.execute_query(query)
            return result[0]["total"] if result else 0
            
        except Exception as e:
            logger.error(f"Erro ao contar brindes excluídos: {e}")
            return 0
