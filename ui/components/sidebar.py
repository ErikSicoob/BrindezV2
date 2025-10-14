# -*- coding: utf-8 -*-
"""
Componente de Menu Lateral
"""
import customtkinter as ctk
from config.settings import COLORS


class Sidebar(ctk.CTkFrame):
    """Menu lateral de navegação"""
    
    def __init__(self, master, on_menu_click, **kwargs):
        super().__init__(master, **kwargs)
        
        self.on_menu_click = on_menu_click
        self.active_button = None
        self.buttons = {}
        
        self.configure(
            width=250,
            corner_radius=0,
            fg_color=COLORS["sidebar_bg"]
        )
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do menu lateral"""
        # Logo / Título
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=20)
        
        title = ctk.CTkLabel(
            title_frame,
            text="🎁 Gestão de\nBrindes",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        )
        title.pack()
        
        # Separador
        separator = ctk.CTkFrame(self, height=2, fg_color=COLORS["primary"])
        separator.pack(fill="x", padx=20, pady=(0, 20))
        
        # Menu items
        menu_items = [
            ("Dashboard", "📊"),
            ("Brindes", "🎁"),
            ("Relatórios", "📈"),
            ("Configurações", "⚙️"),
        ]
        
        for text, icon in menu_items:
            self._create_menu_button(text, icon)
        
        # Spacer
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        # User info
        self._create_user_info()
    
    def _create_menu_button(self, text, icon):
        """Cria botão do menu"""
        button = ctk.CTkButton(
            self,
            text=f"{icon}  {text}",
            font=("Segoe UI", 14),
            height=45,
            corner_radius=8,
            fg_color="transparent",
            hover_color=COLORS["sidebar_hover"],
            text_color="white",
            anchor="w",
            command=lambda t=text: self._on_button_click(t)
        )
        button.pack(fill="x", padx=15, pady=5)
        self.buttons[text] = button
    
    def _create_user_info(self):
        """Cria informações do usuário"""
        from utils.auth import auth_manager
        
        user_frame = ctk.CTkFrame(self, fg_color=COLORS["sidebar_hover"], corner_radius=8)
        user_frame.pack(fill="x", padx=15, pady=20)
        
        user = auth_manager.current_user
        if user:
            name_label = ctk.CTkLabel(
                user_frame,
                text=f"👤 {user['name']}",
                font=("Segoe UI", 12, "bold"),
                text_color="white"
            )
            name_label.pack(padx=15, pady=(10, 5), anchor="w")
            
            branch_label = ctk.CTkLabel(
                user_frame,
                text=f"📍 {user['branch_name']}",
                font=("Segoe UI", 10),
                text_color="#aaaaaa"
            )
            branch_label.pack(padx=15, pady=(0, 5), anchor="w")
            
            profile_label = ctk.CTkLabel(
                user_frame,
                text=f"🔑 {user['profile']}",
                font=("Segoe UI", 10),
                text_color="#aaaaaa"
            )
            profile_label.pack(padx=15, pady=(0, 10), anchor="w")
    
    def _on_button_click(self, menu_name):
        """Handler de clique no botão"""
        # Atualizar visual do botão ativo
        self._update_active_button(menu_name)
        
        # Callback
        if self.on_menu_click:
            self.on_menu_click(menu_name)
    
    def _update_active_button(self, menu_name):
        """Atualiza o visual do botão ativo"""
        if self.active_button:
            self.active_button.configure(fg_color="transparent")
        
        if menu_name in self.buttons:
            self.buttons[menu_name].configure(fg_color=COLORS["primary"])
            self.active_button = self.buttons[menu_name]
    
    def set_active_menu(self, menu_name):
        """Define menu ativo programaticamente (sem chamar callback)"""
        self._update_active_button(menu_name)

# Updated: 2025-10-14 14:28:20
