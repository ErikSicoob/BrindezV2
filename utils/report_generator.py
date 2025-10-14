# -*- coding: utf-8 -*-
"""
Gerador de Relatórios
"""
from database.connection import db
from database.dao import BrindeDAO, BrindeExcluidoDAO, MovimentacaoDAO, TransferenciaDAO
from utils.logger import logger
from datetime import datetime, timedelta
import json


class ReportGenerator:
    """Gerador de relatórios do sistema"""
    
    @staticmethod
    def get_estoque_atual(filial_id=None):
        """Relatório de estoque atual"""
        try:
            query = """
                SELECT 
                    b.descricao,
                    c.nome as categoria,
                    b.quantidade,
                    u.codigo as unidade,
                    b.valor_unitario,
                    b.quantidade * b.valor_unitario as valor_total,
                    f.nome as filial,
                    fo.nome as fornecedor,
                    b.estoque_minimo,
                    CASE WHEN b.quantidade <= b.estoque_minimo THEN 'BAIXO' ELSE 'OK' END as status_estoque
                FROM brindes b
                INNER JOIN categorias c ON b.categoria_id = c.id
                INNER JOIN unidades_medida u ON b.unidade_id = u.id
                INNER JOIN filiais f ON b.filial_id = f.id
                LEFT JOIN fornecedores fo ON b.fornecedor_id = fo.id
            """
            
            params = []
            if filial_id:
                query += " WHERE b.filial_id = ?"
                params.append(filial_id)
            
            query += " ORDER BY f.nome, c.nome, b.descricao"
            
            rows = db.execute_query(query, params)
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro no relatório de estoque: {e}")
            return []
    
    @staticmethod
    def get_movimentacoes(data_inicio=None, data_fim=None, filial_id=None):
        """Relatório de movimentações"""
        try:
            query = """
                SELECT 
                    m.data_movimentacao,
                    m.tipo,
                    b.descricao as brinde,
                    m.quantidade,
                    m.valor_unitario,
                    m.quantidade * m.valor_unitario as valor_total,
                    u.nome as usuario,
                    f.nome as filial,
                    m.justificativa
                FROM movimentacoes m
                INNER JOIN brindes b ON m.brinde_id = b.id
                INNER JOIN usuarios u ON m.usuario_id = u.id
                INNER JOIN filiais f ON b.filial_id = f.id
                WHERE 1=1
            """
            
            params = []
            
            if data_inicio:
                query += " AND DATE(m.data_movimentacao) >= ?"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(m.data_movimentacao) <= ?"
                params.append(data_fim)
            
            if filial_id:
                query += " AND b.filial_id = ?"
                params.append(filial_id)
            
            query += " ORDER BY m.data_movimentacao DESC"
            
            rows = db.execute_query(query, params)
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro no relatório de movimentações: {e}")
            return []
    
    @staticmethod
    def get_transferencias(data_inicio=None, data_fim=None):
        """Relatório de transferências"""
        try:
            query = """
                SELECT 
                    t.data_transferencia,
                    b.descricao as brinde,
                    t.quantidade,
                    fo.nome as filial_origem,
                    fd.nome as filial_destino,
                    u.nome as usuario,
                    t.justificativa
                FROM transferencias t
                INNER JOIN brindes b ON t.brinde_id = b.id
                INNER JOIN filiais fo ON t.filial_origem_id = fo.id
                INNER JOIN filiais fd ON t.filial_destino_id = fd.id
                INNER JOIN usuarios u ON t.usuario_id = u.id
                WHERE 1=1
            """
            
            params = []
            
            if data_inicio:
                query += " AND DATE(t.data_transferencia) >= ?"
                params.append(data_inicio)
            
            if data_fim:
                query += " AND DATE(t.data_transferencia) <= ?"
                params.append(data_fim)
            
            query += " ORDER BY t.data_transferencia DESC"
            
            rows = db.execute_query(query, params)
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro no relatório de transferências: {e}")
            return []
    
    @staticmethod
    def get_estoque_baixo(filial_id=None):
        """Relatório de estoque baixo"""
        try:
            query = """
                SELECT 
                    b.descricao,
                    c.nome as categoria,
                    b.quantidade,
                    b.estoque_minimo,
                    u.codigo as unidade,
                    f.nome as filial,
                    fo.nome as fornecedor
                FROM brindes b
                INNER JOIN categorias c ON b.categoria_id = c.id
                INNER JOIN unidades_medida u ON b.unidade_id = u.id
                INNER JOIN filiais f ON b.filial_id = f.id
                LEFT JOIN fornecedores fo ON b.fornecedor_id = fo.id
                WHERE b.quantidade <= b.estoque_minimo
            """
            
            params = []
            if filial_id:
                query += " AND b.filial_id = ?"
                params.append(filial_id)
            
            query += " ORDER BY f.nome, (b.quantidade - b.estoque_minimo), b.descricao"
            
            rows = db.execute_query(query, params)
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro no relatório de estoque baixo: {e}")
            return []
    
    @staticmethod
    def get_valor_por_categoria(filial_id=None):
        """Relatório de valor por categoria"""
        try:
            query = """
                SELECT 
                    c.nome as categoria,
                    COUNT(b.id) as total_itens,
                    SUM(b.quantidade) as quantidade_total,
                    SUM(b.quantidade * b.valor_unitario) as valor_total,
                    AVG(b.valor_unitario) as valor_medio,
                    f.nome as filial
                FROM brindes b
                INNER JOIN categorias c ON b.categoria_id = c.id
                INNER JOIN filiais f ON b.filial_id = f.id
                WHERE 1=1
            """
            
            params = []
            if filial_id:
                query += " AND b.filial_id = ?"
                params.append(filial_id)
            
            query += """
                GROUP BY c.id, c.nome, f.id, f.nome
                ORDER BY valor_total DESC
            """
            
            rows = db.execute_query(query, params)
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro no relatório de valor por categoria: {e}")
            return []
    
    @staticmethod
    def get_usuarios_report():
        """Relatório de usuários"""
        try:
            query = """
                SELECT 
                    u.nome,
                    u.username,
                    u.email,
                    u.perfil,
                    f.nome as filial,
                    CASE WHEN u.ativo = 1 THEN 'ATIVO' ELSE 'INATIVO' END as status,
                    u.created_at as data_criacao,
                    COUNT(m.id) as total_movimentacoes
                FROM usuarios u
                INNER JOIN filiais f ON u.filial_id = f.id
                LEFT JOIN movimentacoes m ON u.id = m.usuario_id
                GROUP BY u.id, u.nome, u.username, u.email, u.perfil, f.nome, u.ativo, u.created_at
                ORDER BY f.nome, u.nome
            """
            
            rows = db.execute_query(query)
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Erro no relatório de usuários: {e}")
            return []
    
    @staticmethod
    def get_historico_item(brinde_id):
        """Histórico completo de um item"""
        try:
            # Buscar informações do brinde
            brinde_query = """
                SELECT b.*, c.nome as categoria, u.codigo as unidade, 
                       f.nome as filial, fo.nome as fornecedor
                FROM brindes b
                INNER JOIN categorias c ON b.categoria_id = c.id
                INNER JOIN unidades_medida u ON b.unidade_id = u.id
                INNER JOIN filiais f ON b.filial_id = f.id
                LEFT JOIN fornecedores fo ON b.fornecedor_id = fo.id
                WHERE b.id = ?
            """
            
            brinde_rows = db.execute_query(brinde_query, (brinde_id,))
            if not brinde_rows:
                return {"brinde": None, "movimentacoes": [], "transferencias": []}
            
            brinde = dict(brinde_rows[0])
            
            # Buscar movimentações
            mov_query = """
                SELECT m.*, u.nome as usuario
                FROM movimentacoes m
                INNER JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.brinde_id = ?
                ORDER BY m.data_movimentacao DESC
            """
            
            mov_rows = db.execute_query(mov_query, (brinde_id,))
            movimentacoes = [dict(row) for row in mov_rows]
            
            # Buscar transferências
            trans_query = """
                SELECT t.*, u.nome as usuario, fo.nome as filial_origem, fd.nome as filial_destino
                FROM transferencias t
                INNER JOIN usuarios u ON t.usuario_id = u.id
                INNER JOIN filiais fo ON t.filial_origem_id = fo.id
                INNER JOIN filiais fd ON t.filial_destino_id = fd.id
                WHERE t.brinde_id = ?
                ORDER BY t.data_transferencia DESC
            """
            
            trans_rows = db.execute_query(trans_query, (brinde_id,))
            transferencias = [dict(row) for row in trans_rows]
            
            return {
                "brinde": brinde,
                "movimentacoes": movimentacoes,
                "transferencias": transferencias
            }
            
        except Exception as e:
            logger.error(f"Erro no histórico do item: {e}")
            return {"brinde": None, "movimentacoes": [], "transferencias": []}
    
    @staticmethod
    def get_dashboard_stats():
        """Estatísticas para o dashboard"""
        try:
            stats = {}
            
            # Total de brindes
            total_query = "SELECT COUNT(*) as total FROM brindes"
            result = db.execute_query(total_query)
            stats["total_brindes"] = result[0]["total"] if result else 0
            
            # Valor total do estoque
            valor_query = "SELECT SUM(quantidade * valor_unitario) as valor_total FROM brindes"
            result = db.execute_query(valor_query)
            stats["valor_total"] = result[0]["valor_total"] or 0
            
            # Itens com estoque baixo
            baixo_query = "SELECT COUNT(*) as total FROM brindes WHERE quantidade <= estoque_minimo"
            result = db.execute_query(baixo_query)
            stats["estoque_baixo"] = result[0]["total"] if result else 0
            
            # Movimentações hoje
            hoje = datetime.now().strftime("%Y-%m-%d")
            mov_query = "SELECT COUNT(*) as total FROM movimentacoes WHERE DATE(data_movimentacao) = ?"
            result = db.execute_query(mov_query, (hoje,))
            stats["movimentacoes_hoje"] = result[0]["total"] if result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro nas estatísticas do dashboard: {e}")
            return {}


# Instância global
report_generator = ReportGenerator()

# Updated: 2025-10-14 14:28:20
