# -*- coding: utf-8 -*-
"""
Componente de Breadcrumb
"""
import customtkinter as ctk
from config.settings import COLORS


class Breadcrumb(ctk.CTkFrame):
    """Breadcrumb para navegação"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(
            height=50,
            fg_color="white",
            corner_radius=0
        )
        
        self.label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["dark"]
        )
        self.label.pack(side="left", padx=20, pady=10)
    
    def set_path(self, path):
        """Define o caminho do breadcrumb"""
        self.label.configure(text=f"📍 {path}")

# Updated: 2025-10-14 14:28:20
