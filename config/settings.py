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

# Cores do Tema - Nova Identidade Visual
COLORS = {
    # Cores Principais
    "primary": "#00AE9D",           # Turquesa
    "primary_dark": "#007870",      # Turquesa escuro (hover)
    "primary_light": "#00C6B1",     # Turquesa claro (hover)
    "secondary": "#003641",         # Verde escuro
    "secondary_dark": "#00515E",    # Verde escuro (hover)
    
    # Cores de Suporte
    "accent": "#C9D200",            # Verde claro
    "accent_medium": "#7DB61C",     # Verde médio
    "accent_purple": "#49479D",     # Roxo
    "accent_purple_hover": "#5B58B3", # Roxo hover
    
    # Cores Funcionais
    "danger": "#49479D",            # Roxo (substituindo vermelho)
    "warning": "#C9D200",           # Verde claro
    "success": "#7DB61C",           # Verde médio
    "info": "#00AE9D",              # Turquesa
    
    # Cores Neutras
    "dark": "#003641",              # Verde escuro
    "text_dark": "#2C2C2C",         # Cinza escuro
    "light": "#F5F7FA",             # Cinza claro
    "white": "#FFFFFF",             # Branco
    
    # Interface
    "sidebar_bg": "#003641",        # Verde escuro
    "sidebar_hover": "#00AE9D",     # Turquesa
    "sidebar_active": "#00AE9D",    # Turquesa
    "sidebar_text": "#FFFFFF",      # Branco
    "content_bg": "#F5F7FA",        # Cinza claro
    
    # Cards e Containers
    "card_bg": "#FFFFFF",           # Branco
    "card_border": "#E1E5EA",       # Cinza médio
    "card_text": "#003641",         # Verde escuro
    
    # Inputs e Forms
    "input_bg": "#FFFFFF",          # Branco
    "input_border": "#E1E5EA",      # Cinza médio
    "input_text": "#003641",        # Verde escuro
    "input_placeholder": "#7DB61C", # Verde médio
    
    # Outros
    "border": "#E1E5EA",            # Cinza médio
    "hover": "#F5F7FA",             # Cinza claro
    "disabled": "#A0A0A0"           # Cinza desabilitado
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
def get_db_path():
    """Obtém o caminho do banco de dados (configurado pelo usuário ou padrão)"""
    try:
        from config.user_settings import user_settings
        user_path = user_settings.get_db_path()
        return user_path if user_path else "data/brindes.db"
    except:
        return "data/brindes.db"

# Caminho padrão do banco (pode ser sobrescrito pelo usuário)
DB_PATH = get_db_path()

# Updated: 2025-10-15 11:24:00
