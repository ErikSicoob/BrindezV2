# -*- coding: utf-8 -*-
"""
Módulo de Importação de Dados
Suporta importação de Excel e CSV
"""
import pandas as pd
from utils.logger import logger
from database.dao import *


class DataImporter:
    """Classe para importação de dados"""
    
    @staticmethod
    def read_excel(filepath, sheet_name=0):
        """
        Lê arquivo Excel e retorna DataFrame
        
        Args:
            filepath: Caminho do arquivo
            sheet_name: Nome ou índice da planilha
            
        Returns:
            DataFrame ou None em caso de erro
        """
        try:
            df = pd.read_excel(filepath, sheet_name=sheet_name)
            logger.info(f"Arquivo Excel lido: {filepath} ({len(df)} linhas)")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler Excel: {e}")
            return None
    
    @staticmethod
    def read_csv(filepath, delimiter=';', encoding='utf-8-sig'):
        """
        Lê arquivo CSV e retorna DataFrame
        
        Args:
            filepath: Caminho do arquivo
            delimiter: Delimitador do CSV
            encoding: Codificação do arquivo
            
        Returns:
            DataFrame ou None em caso de erro
        """
        try:
            df = pd.read_csv(filepath, sep=delimiter, encoding=encoding)
            logger.info(f"Arquivo CSV lido: {filepath} ({len(df)} linhas)")
            return df
        except Exception as e:
            logger.error(f"Erro ao ler CSV: {e}")
            return None
    
    @staticmethod
    def import_brindes(df, filial_id):
        """
        Importa brindes de um DataFrame
        
        Colunas esperadas:
        - descricao (obrigatório)
        - quantidade (obrigatório)
        - valor_unitario (obrigatório)
        - categoria (obrigatório)
        - unidade (obrigatório)
        - fornecedor (opcional)
        - codigo_interno (opcional)
        - estoque_minimo (opcional)
        - observacoes (opcional)
        
        Returns:
            dict: {"success": int, "errors": list}
        """
        success_count = 0
        errors = []
        
        try:
            # Validar colunas obrigatórias
            required_cols = ['descricao', 'quantidade', 'valor_unitario', 'categoria', 'unidade']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                return {
                    "success": 0,
                    "errors": [f"Colunas obrigatórias faltando: {', '.join(missing_cols)}"]
                }
            
            # Buscar categorias, unidades e fornecedores existentes
            categorias = {c['nome']: c['id'] for c in CategoriaDAO.get_all()}
            unidades = {u['codigo']: u['id'] for u in UnidadeDAO.get_all()}
            fornecedores = {f['nome']: f['id'] for f in FornecedorDAO.get_all()}
            
            # Processar cada linha
            for idx, row in df.iterrows():
                try:
                    # Validar categoria
                    categoria_nome = str(row['categoria']).strip()
                    if categoria_nome not in categorias:
                        errors.append(f"Linha {idx + 2}: Categoria '{categoria_nome}' não encontrada")
                        continue
                    
                    # Validar unidade
                    unidade_codigo = str(row['unidade']).strip()
                    if unidade_codigo not in unidades:
                        errors.append(f"Linha {idx + 2}: Unidade '{unidade_codigo}' não encontrada")
                        continue
                    
                    # Fornecedor (opcional)
                    fornecedor_id = None
                    if 'fornecedor' in row and pd.notna(row['fornecedor']):
                        fornecedor_nome = str(row['fornecedor']).strip()
                        fornecedor_id = fornecedores.get(fornecedor_nome)
                    
                    # Criar brinde
                    data = {
                        "descricao": str(row['descricao']).strip(),
                        "quantidade": int(row['quantidade']),
                        "valor_unitario": float(row['valor_unitario']),
                        "categoria_id": categorias[categoria_nome],
                        "unidade_id": unidades[unidade_codigo],
                        "filial_id": filial_id,
                        "fornecedor_id": fornecedor_id,
                        "codigo_interno": str(row.get('codigo_interno', '')).strip() or None,
                        "estoque_minimo": int(row.get('estoque_minimo', 10)),
                        "observacoes": str(row.get('observacoes', '')).strip() or None
                    }
                    
                    BrindeDAO.create(data)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Linha {idx + 2}: {str(e)}")
            
            logger.info(f"Importação concluída: {success_count} sucesso, {len(errors)} erros")
            return {"success": success_count, "errors": errors}
            
        except Exception as e:
            logger.error(f"Erro na importação de brindes: {e}")
            return {"success": 0, "errors": [str(e)]}
    
    @staticmethod
    def import_categorias(df):
        """
        Importa categorias de um DataFrame
        
        Colunas esperadas:
        - nome (obrigatório)
        - descricao (opcional)
        
        Returns:
            dict: {"success": int, "errors": list}
        """
        success_count = 0
        errors = []
        
        try:
            if 'nome' not in df.columns:
                return {"success": 0, "errors": ["Coluna 'nome' obrigatória não encontrada"]}
            
            for idx, row in df.iterrows():
                try:
                    data = {
                        "nome": str(row['nome']).strip(),
                        "descricao": str(row.get('descricao', '')).strip() or None
                    }
                    
                    CategoriaDAO.create(data)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Linha {idx + 2}: {str(e)}")
            
            return {"success": success_count, "errors": errors}
            
        except Exception as e:
            logger.error(f"Erro na importação de categorias: {e}")
            return {"success": 0, "errors": [str(e)]}
    
    @staticmethod
    def import_fornecedores(df):
        """
        Importa fornecedores de um DataFrame
        
        Colunas esperadas:
        - nome (obrigatório)
        - cnpj (opcional)
        - contato (opcional)
        - telefone (opcional)
        - email (opcional)
        - endereco (opcional)
        - cidade (opcional)
        - estado (opcional)
        - cep (opcional)
        - observacoes (opcional)
        
        Returns:
            dict: {"success": int, "errors": list}
        """
        success_count = 0
        errors = []
        
        try:
            if 'nome' not in df.columns:
                return {"success": 0, "errors": ["Coluna 'nome' obrigatória não encontrada"]}
            
            for idx, row in df.iterrows():
                try:
                    data = {
                        "nome": str(row['nome']).strip(),
                        "cnpj": str(row.get('cnpj', '')).strip() or None,
                        "contato": str(row.get('contato', '')).strip() or None,
                        "telefone": str(row.get('telefone', '')).strip() or None,
                        "email": str(row.get('email', '')).strip() or None,
                        "endereco": str(row.get('endereco', '')).strip() or None,
                        "cidade": str(row.get('cidade', '')).strip() or None,
                        "estado": str(row.get('estado', '')).strip() or None,
                        "cep": str(row.get('cep', '')).strip() or None,
                        "observacoes": str(row.get('observacoes', '')).strip() or None
                    }
                    
                    FornecedorDAO.create(data)
                    success_count += 1
                    
                except Exception as e:
                    errors.append(f"Linha {idx + 2}: {str(e)}")
            
            return {"success": success_count, "errors": errors}
            
        except Exception as e:
            logger.error(f"Erro na importação de fornecedores: {e}")
            return {"success": 0, "errors": [str(e)]}
    
    @staticmethod
    def get_template_brindes():
        """Retorna DataFrame template para importação de brindes"""
        return pd.DataFrame({
            'descricao': ['Exemplo de Brinde'],
            'quantidade': [100],
            'valor_unitario': [10.50],
            'categoria': ['Escritório'],
            'unidade': ['UN'],
            'fornecedor': ['Nome do Fornecedor'],
            'codigo_interno': ['BRI-001'],
            'estoque_minimo': [10],
            'observacoes': ['Observações opcionais']
        })
    
    @staticmethod
    def get_template_categorias():
        """Retorna DataFrame template para importação de categorias"""
        return pd.DataFrame({
            'nome': ['Categoria Exemplo'],
            'descricao': ['Descrição da categoria']
        })
    
    @staticmethod
    def get_template_fornecedores():
        """Retorna DataFrame template para importação de fornecedores"""
        return pd.DataFrame({
            'nome': ['Fornecedor Exemplo'],
            'cnpj': ['12.345.678/0001-90'],
            'contato': ['João Silva'],
            'telefone': ['(11) 1234-5678'],
            'email': ['contato@fornecedor.com'],
            'endereco': ['Rua Exemplo, 123'],
            'cidade': ['São Paulo'],
            'estado': ['SP'],
            'cep': ['01000-000'],
            'observacoes': ['Observações opcionais']
        })


# Instância global
data_importer = DataImporter()

# Updated: 2025-10-14 14:28:20
