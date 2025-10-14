# -*- coding: utf-8 -*-
"""
Módulo de Exportação de Dados
Suporta exportação para Excel e CSV
"""
import pandas as pd
from datetime import datetime
import os
from utils.logger import logger


class DataExporter:
    """Classe para exportação de dados"""
    
    @staticmethod
    def export_to_excel(data, filename, sheet_name="Dados"):
        """
        Exporta dados para Excel
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (sem extensão)
            sheet_name: Nome da planilha
            
        Returns:
            str: Caminho do arquivo gerado ou None em caso de erro
        """
        try:
            if not data:
                logger.warning("Nenhum dado para exportar")
                return None
            
            # Criar DataFrame
            df = pd.DataFrame(data)
            
            # Criar diretório de exportação se não existir
            export_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(export_dir, f"{filename}_{timestamp}.xlsx")
            
            # Exportar para Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Ajustar largura das colunas
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    )
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            logger.info(f"Dados exportados para: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao exportar para Excel: {e}")
            return None
    
    @staticmethod
    def export_to_csv(data, filename, delimiter=';', encoding='utf-8-sig'):
        """
        Exporta dados para CSV
        
        Args:
            data: Lista de dicionários com os dados
            filename: Nome do arquivo (sem extensão)
            delimiter: Delimitador do CSV (padrão: ;)
            encoding: Codificação do arquivo (padrão: utf-8-sig para Excel)
            
        Returns:
            str: Caminho do arquivo gerado ou None em caso de erro
        """
        try:
            if not data:
                logger.warning("Nenhum dado para exportar")
                return None
            
            # Criar DataFrame
            df = pd.DataFrame(data)
            
            # Criar diretório de exportação se não existir
            export_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(export_dir, f"{filename}_{timestamp}.csv")
            
            # Exportar para CSV
            df.to_csv(filepath, sep=delimiter, index=False, encoding=encoding)
            
            logger.info(f"Dados exportados para: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao exportar para CSV: {e}")
            return None
    
    @staticmethod
    def export_multiple_sheets(data_dict, filename):
        """
        Exporta múltiplas planilhas em um único arquivo Excel
        
        Args:
            data_dict: Dicionário onde a chave é o nome da planilha e o valor são os dados
            filename: Nome do arquivo (sem extensão)
            
        Returns:
            str: Caminho do arquivo gerado ou None em caso de erro
        """
        try:
            if not data_dict:
                logger.warning("Nenhum dado para exportar")
                return None
            
            # Criar diretório de exportação se não existir
            export_dir = os.path.join(os.getcwd(), "exports")
            os.makedirs(export_dir, exist_ok=True)
            
            # Nome do arquivo com timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(export_dir, f"{filename}_{timestamp}.xlsx")
            
            # Exportar para Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, data in data_dict.items():
                    if data:
                        df = pd.DataFrame(data)
                        df.to_excel(writer, sheet_name=sheet_name[:31], index=False)  # Limite de 31 caracteres
                        
                        # Ajustar largura das colunas
                        worksheet = writer.sheets[sheet_name[:31]]
                        for idx, col in enumerate(df.columns):
                            max_length = max(
                                df[col].astype(str).apply(len).max(),
                                len(str(col))
                            )
                            worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
            
            logger.info(f"Dados exportados para: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Erro ao exportar múltiplas planilhas: {e}")
            return None


# Instância global
data_exporter = DataExporter()

# Updated: 2025-10-14 14:28:20
