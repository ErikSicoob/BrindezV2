# -*- coding: utf-8 -*-
"""
Gerenciador de Configurações do Usuário
Armazena configurações persistentes em arquivo JSON
"""
import json
import os
from pathlib import Path


class UserSettingsManager:
    """Gerenciador de configurações persistentes"""
    
    def __init__(self):
        # Define o caminho do arquivo de configurações na pasta config
        self.config_file = Path(__file__).parent / "user_config.json"
        self._settings = self._load_settings()
    
    def _load_settings(self):
        """Carrega configurações do arquivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                return {}
        return {}
    
    def _save_settings(self):
        """Salva configurações no arquivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def get(self, key, default=None):
        """Obtém valor de uma configuração"""
        return self._settings.get(key, default)
    
    def set(self, key, value):
        """Define valor de uma configuração"""
        self._settings[key] = value
        return self._save_settings()
    
    def get_db_path(self):
        """Obtém caminho do banco de dados configurado"""
        return self.get('db_path', None)
    
    def set_db_path(self, path):
        """Define caminho do banco de dados"""
        return self.set('db_path', path)
    
    def get_min_stock_alert(self):
        """Obtém quantidade mínima para alerta de estoque"""
        return self.get('min_stock_alert', 10)
    
    def set_min_stock_alert(self, quantity):
        """Define quantidade mínima para alerta de estoque"""
        return self.set('min_stock_alert', int(quantity))


# Instância global
user_settings = UserSettingsManager()
