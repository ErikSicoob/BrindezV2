# -*- coding: utf-8 -*-
"""
Configurações do Sistema de Gestão de Brindes
"""

# Configurações da Aplicação
APP_NAME = "Sistema de Gestão de Brindes"
APP_VERSION = "1.0.0"

# Configurações da Interface
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 600

# Cores do Tema
COLORS = {
    "primary": "#1f6aa5",
    "primary_dark": "#144870",
    "secondary": "#2fa572",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "success": "#28a745",
    "info": "#17a2b8",
    "dark": "#343a40",
    "light": "#f8f9fa",
    "sidebar_bg": "#2b2b2b",
    "sidebar_hover": "#3d3d3d",
    "content_bg": "#f5f5f5"
}

# Configurações de Estoque
DEFAULT_MIN_STOCK_ALERT = 10
DEFAULT_ITEMS_PER_PAGE = 20

# Perfis de Usuário
USER_PROFILES = {
    "ADMIN": "Administrador",
    "GESTOR": "Gestor",
    "USUARIO": "Usuário"
}

# Unidades de Medida Padrão
DEFAULT_UNITS = ["UN", "KG", "LT", "CX", "PC", "MT", "M²", "M³"]

# Categorias Padrão
DEFAULT_CATEGORIES = [
    "Escritório",
    "Tecnologia",
    "Vestuário",
    "Acessórios",
    "Material Promocional",
    "Outros"
]

# Configurações do Banco de Dados
DB_PATH = "data/brindes.db"
