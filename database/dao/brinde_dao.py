# -*- coding: utf-8 -*-
"""
DAO para Brindes
"""
from database.connection import db


class BrindeDAO:
    """Data Access Object para Brindes"""
    
    @staticmethod
    def create(data):
        """Cria um novo brinde"""
        query = """
            INSERT INTO brindes (
                descricao, quantidade, valor_unitario, categoria_id,
                unidade_id, filial_id, fornecedor_id, codigo_interno,
                observacoes, estoque_minimo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            data.get('descricao'),
            data.get('quantidade', 0),
            data.get('valor_unitario'),
            data.get('categoria_id'),
            data.get('unidade_id'),
            data.get('filial_id'),
            data.get('fornecedor_id'),
            data.get('codigo_interno'),
            data.get('observacoes'),
            data.get('estoque_minimo', 10)
        )
        return db.execute_update(query, params)
    
    @staticmethod
    def get_all(filial_id=None):
        """Retorna todos os brindes"""
        query = "SELECT * FROM vw_estoque_atual"
        params = None
        
        if filial_id:
            query += " WHERE filial_id = ?"
            params = (filial_id,)
        
        query += " ORDER BY descricao"
        
        rows = db.execute_query(query, params)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_id(brinde_id):
        """Retorna brinde por ID"""
        query = "SELECT * FROM brindes WHERE id = ?"
        rows = db.execute_query(query, (brinde_id,))
        return dict(rows[0]) if rows else None
    
    @staticmethod
    def get_by_category(categoria_id, filial_id=None):
        """Retorna brindes por categoria"""
        query = "SELECT * FROM brindes WHERE categoria_id = ?"
        params = [categoria_id]
        
        if filial_id:
            query += " AND filial_id = ?"
            params.append(filial_id)
        
        rows = db.execute_query(query, tuple(params))
        return [dict(row) for row in rows]
    
    @staticmethod
    def update(brinde_id, data):
        """Atualiza um brinde"""
        query = """
            UPDATE brindes SET
                descricao = ?, valor_unitario = ?, categoria_id = ?,
                unidade_id = ?, fornecedor_id = ?, codigo_interno = ?,
                observacoes = ?, estoque_minimo = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        params = (
            data.get('descricao'),
            data.get('valor_unitario'),
            data.get('categoria_id'),
            data.get('unidade_id'),
            data.get('fornecedor_id'),
            data.get('codigo_interno'),
            data.get('observacoes'),
            data.get('estoque_minimo', 10),
            brinde_id
        )
        db.execute_update(query, params)
        return True
    
    @staticmethod
    def delete(brinde_id):
        """Exclui um brinde"""
        query = "DELETE FROM brindes WHERE id = ?"
        db.execute_update(query, (brinde_id,))
        return True
    
    @staticmethod
    def add_stock(brinde_id, quantidade, valor_unitario=None):
        """Adiciona estoque"""
        # Atualizar quantidade
        query = "UPDATE brindes SET quantidade = quantidade + ?"
        params = [quantidade]
        
        # Atualizar valor unitário se fornecido
        if valor_unitario is not None:
            query += ", valor_unitario = ?"
            params.append(valor_unitario)
        
        query += ", updated_at = CURRENT_TIMESTAMP WHERE id = ?"
        params.append(brinde_id)
        
        db.execute_update(query, tuple(params))
        return True
    
    @staticmethod
    def remove_stock(brinde_id, quantidade):
        """Remove estoque"""
        # Verificar se há estoque suficiente
        brinde = BrindeDAO.get_by_id(brinde_id)
        if not brinde or brinde['quantidade'] < quantidade:
            return False
        
        query = """
            UPDATE brindes SET 
                quantidade = quantidade - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """
        db.execute_update(query, (quantidade, brinde_id))
        return True
    
    @staticmethod
    def transfer(brinde_id, filial_destino_id, quantidade):
        """Transfere brinde para outra filial"""
        # Verificar estoque
        brinde = BrindeDAO.get_by_id(brinde_id)
        if not brinde or brinde['quantidade'] < quantidade:
            return False
        
        # Remover da filial origem
        BrindeDAO.remove_stock(brinde_id, quantidade)
        
        # Verificar se já existe na filial destino
        query = """
            SELECT id FROM brindes 
            WHERE descricao = ? AND categoria_id = ? AND filial_id = ?
        """
        rows = db.execute_query(query, (
            brinde['descricao'],
            brinde['categoria_id'],
            filial_destino_id
        ))
        
        if rows:
            # Adicionar ao existente
            BrindeDAO.add_stock(rows[0]['id'], quantidade, brinde['valor_unitario'])
        else:
            # Criar novo registro na filial destino
            novo_brinde = {
                'descricao': brinde['descricao'],
                'quantidade': quantidade,
                'valor_unitario': brinde['valor_unitario'],
                'categoria_id': brinde['categoria_id'],
                'unidade_id': brinde['unidade_id'],
                'filial_id': filial_destino_id,
                'fornecedor_id': brinde.get('fornecedor_id'),
                'codigo_interno': brinde.get('codigo_interno'),
                'observacoes': brinde.get('observacoes'),
                'estoque_minimo': brinde.get('estoque_minimo', 10)
            }
            BrindeDAO.create(novo_brinde)
        
        return True
    
    @staticmethod
    def get_low_stock(filial_id=None):
        """Retorna itens com estoque baixo"""
        query = "SELECT * FROM vw_estoque_atual WHERE estoque_baixo = 1"
        params = None
        
        if filial_id:
            query += " AND filial_id = ?"
            params = (filial_id,)
        
        rows = db.execute_query(query, params)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_stats(filial_id=None):
        """Retorna estatísticas de estoque"""
        query = """
            SELECT 
                COUNT(*) as total_produtos,
                SUM(quantidade) as total_itens,
                SUM(valor_total) as valor_total,
                SUM(estoque_baixo) as itens_estoque_baixo
            FROM vw_estoque_atual
        """
        params = None
        
        if filial_id:
            query += " WHERE filial_id = ?"
            params = (filial_id,)
        
        rows = db.execute_query(query, params)
        return dict(rows[0]) if rows else {}
    
    @staticmethod
    def get_by_category_stats(filial_id=None):
        """Retorna estatísticas por categoria"""
        query = """
            SELECT 
                categoria,
                COUNT(*) as total_produtos,
                SUM(quantidade) as total_itens,
                SUM(valor_total) as valor_total
            FROM vw_estoque_atual
        """
        
        if filial_id:
            query += " WHERE filial_id = ?"
        
        query += " GROUP BY categoria ORDER BY categoria"
        
        params = (filial_id,) if filial_id else None
        rows = db.execute_query(query, params)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_grouped_by_description():
        """Retorna brindes agrupados por descrição (apenas com quantidade > 0)"""
        query = """
            SELECT 
                b.descricao,
                b.codigo_interno,
                c.nome as categoria,
                u.codigo as unidade,
                fo.nome as fornecedor,
                COUNT(DISTINCT CASE WHEN b.quantidade > 0 THEN b.filial_id END) as num_filiais,
                SUM(CASE WHEN b.quantidade > 0 THEN b.quantidade ELSE 0 END) as quantidade_total,
                AVG(CASE WHEN b.quantidade > 0 THEN b.valor_unitario END) as valor_medio,
                SUM(CASE WHEN b.quantidade > 0 THEN b.quantidade * b.valor_unitario ELSE 0 END) as valor_total
            FROM brindes b
            LEFT JOIN categorias c ON b.categoria_id = c.id
            LEFT JOIN unidades_medida u ON b.unidade_id = u.id
            LEFT JOIN fornecedores fo ON b.fornecedor_id = fo.id
            GROUP BY b.descricao, b.codigo_interno, c.nome, u.codigo, fo.nome
            HAVING quantidade_total > 0
            ORDER BY b.descricao
        """
        rows = db.execute_query(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    def get_by_description(descricao):
        """Retorna todos os registros de um brinde (por descrição) em todas as filiais"""
        query = """
            SELECT 
                b.*,
                c.nome as categoria,
                u.codigo as unidade,
                f.numero as filial_numero,
                f.nome as filial,
                fo.nome as fornecedor,
                (b.quantidade * b.valor_unitario) as valor_total
            FROM brindes b
            LEFT JOIN categorias c ON b.categoria_id = c.id
            LEFT JOIN unidades_medida u ON b.unidade_id = u.id
            LEFT JOIN filiais f ON b.filial_id = f.id
            LEFT JOIN fornecedores fo ON b.fornecedor_id = fo.id
            WHERE b.descricao = ? AND b.quantidade > 0
            ORDER BY f.numero
        """
        rows = db.execute_query(query, (descricao,))
        return [dict(row) for row in rows]
    
    @staticmethod
    def create_multi_filial(data, distribuicao):
        """
        Cria brinde em múltiplas filiais
        
        Args:
            data: dict com dados do brinde (sem filial_id e quantidade)
            distribuicao: dict {filial_id: quantidade}
        
        Returns:
            list de IDs criados
        """
        ids_criados = []
        
        for filial_id, quantidade in distribuicao.items():
            brinde_data = data.copy()
            brinde_data['filial_id'] = filial_id
            brinde_data['quantidade'] = quantidade
            
            brinde_id = BrindeDAO.create(brinde_data)
            ids_criados.append(brinde_id)
        
        return ids_criados

# Updated: 2025-10-15 14:17:00
