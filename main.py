# -*- coding: utf-8 -*-
"""
Sistema de Gestão de Brindes
Arquivo Principal
"""
import customtkinter as ctk
from config.settings import *
from utils.auth import auth_manager
from utils.logger import logger, info, error, warning
from ui.components.sidebar import Sidebar
from ui.components.breadcrumb import Breadcrumb
from ui.views.dashboard_view import DashboardView
from ui.views.brindes_view import BrindesView
from ui.views.relatorios_view import RelatoriosView
from ui.views.configuracoes_view import ConfiguracoesView


class App(ctk.CTk):
    """Aplicação Principal"""
    
    def __init__(self):
        super().__init__()
        
        info("=" * 60)
        info(f"Iniciando {APP_NAME} v{APP_VERSION}")
        info("=" * 60)
        
        try:
            # Configurar janela
            self.title(APP_NAME)
            self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
            info(f"Janela configurada: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            
            # Configurar tema
            ctk.set_appearance_mode("light")
            ctk.set_default_color_theme("blue")
            info("Tema configurado: light mode")
            
            # Autenticar usuário
            info("Autenticando usuário...")
            user = auth_manager.authenticate()
            
            if not user:
                error("Falha na autenticação: Usuário não encontrado e não foi possível criar usuário temporário")
                error("Verifique se existem filiais cadastradas no banco de dados")
                raise Exception("Falha na autenticação do usuário")
            
            info(f"Usuário autenticado: {user['name']} ({user['profile']}) - Filial: {user['branch_name']}")
            
            # Criar interface
            info("Criando interface...")
            self._create_layout()
            info("Interface criada com sucesso")
            
            # Mostrar dashboard inicial
            info("Carregando Dashboard...")
            self.show_view("Dashboard")
            
            # Maximizar janela após tudo estar carregado
            self.after(100, lambda: self.state('zoomed'))
            
            info("Sistema iniciado com sucesso!")
            
        except Exception as e:
            error(f"Erro ao iniciar aplicação: {e}")
            import traceback
            error(traceback.format_exc())
            raise
    
    def _create_layout(self):
        """Cria layout principal"""
        # Grid principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Menu lateral
        self.sidebar = Sidebar(self, on_menu_click=self.show_view)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Container de conteúdo
        self.content_container = ctk.CTkFrame(self, fg_color=COLORS["content_bg"], corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        
        # Breadcrumb
        self.breadcrumb = Breadcrumb(self.content_container)
        self.breadcrumb.pack(fill="x")
        
        # Container de views
        self.views_container = ctk.CTkFrame(self.content_container, fg_color="transparent")
        self.views_container.pack(fill="both", expand=True)
        
        # Dicionário de views
        self.views = {}
    
    def show_view(self, view_name):
        """Mostra a view selecionada"""
        try:
            info(f"Navegando para: {view_name}")
            
            # Limpar container
            for widget in self.views_container.winfo_children():
                widget.destroy()
            
            # Atualizar breadcrumb
            self.breadcrumb.set_path(view_name)
            
            # Criar ou recuperar view
            if view_name == "Dashboard":
                view = DashboardView(self.views_container)
            elif view_name == "Brindes":
                view = BrindesView(self.views_container)
            elif view_name == "Relatórios":
                view = RelatoriosView(self.views_container)
            elif view_name == "Configurações":
                view = ConfiguracoesView(self.views_container)
            else:
                warning(f"View '{view_name}' não implementada")
                view = ctk.CTkLabel(
                    self.views_container,
                    text=f"View '{view_name}' em desenvolvimento",
                    font=("Segoe UI", 18)
                )
            
            view.pack(fill="both", expand=True)
            
            # Atualizar menu ativo
            self.sidebar.set_active_menu(view_name)
            
            info(f"View '{view_name}' carregada com sucesso")
            
        except Exception as e:
            error(f"Erro ao carregar view '{view_name}': {e}")
            import traceback
            error(traceback.format_exc())


def main():
    """Função principal"""
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

# Updated: 2025-10-14 14:28:20
