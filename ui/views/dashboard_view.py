# -*- coding: utf-8 -*-
"""
Tela de Dashboard
"""
import customtkinter as ctk
from config.settings import COLORS
from utils.auth import auth_manager
from database.dao import BrindeDAO


class DashboardView(ctk.CTkFrame):
    """View do Dashboard com indicadores"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLORS["content_bg"])
        
        self._create_widgets()
        self.load_data()
    
    def _create_widgets(self):
        """Cria os widgets do dashboard"""
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Grid de cards
        self.cards_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        self.cards_frame.pack(fill="x", pady=(0, 20))
        
        # Configurar grid
        for i in range(4):
            self.cards_frame.grid_columnconfigure(i, weight=1)
        
        # Cards de estatísticas
        self.total_items_card = self._create_stat_card(
            self.cards_frame, "Total de Itens", "0", "📦", COLORS["primary"], 0
        )
        
        self.total_products_card = self._create_stat_card(
            self.cards_frame, "Produtos Cadastrados", "0", "🎁", COLORS["info"], 1
        )
        
        self.total_value_card = self._create_stat_card(
            self.cards_frame, "Valor Total", "R$ 0,00", "💰", COLORS["success"], 2
        )
        
        self.low_stock_card = self._create_stat_card(
            self.cards_frame, "Estoque Baixo", "0", "⚠️", COLORS["warning"], 3
        )
        
        # Seção de categorias
        categories_frame = ctk.CTkFrame(main_container, fg_color="white", corner_radius=10)
        categories_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = ctk.CTkLabel(
            categories_frame,
            text="📊 Itens por Categoria",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["dark"]
        )
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        
        # Container de categorias
        self.categories_container = ctk.CTkFrame(categories_frame, fg_color="transparent")
        self.categories_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def _create_stat_card(self, parent, title, value, icon, color, column):
        """Cria um card de estatística"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10, height=120)
        card.grid(row=0, column=column, padx=10, pady=10, sticky="nsew")
        
        # Ícone
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI", 40)
        )
        icon_label.pack(pady=(15, 5))
        
        # Valor
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=("Segoe UI", 22, "bold"),
            text_color=color
        )
        value_label.pack()
        
        # Título
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 11),
            text_color="#666666"
        )
        title_label.pack(pady=(0, 15))
        
        return {"card": card, "value": value_label, "title": title_label}
    
    def _create_category_row(self, parent, category_name, quantity, percentage):
        """Cria uma linha de categoria"""
        row = ctk.CTkFrame(parent, fg_color="transparent", height=50)
        row.pack(fill="x", pady=5)
        
        # Nome da categoria
        name_label = ctk.CTkLabel(
            row,
            text=category_name,
            font=("Segoe UI", 12),
            text_color=COLORS["dark"]
        )
        name_label.pack(side="left", padx=(0, 20))
        
        # Barra de progresso
        progress_frame = ctk.CTkFrame(row, fg_color="#e0e0e0", height=25, corner_radius=5)
        progress_frame.pack(side="left", fill="x", expand=True)
        
        if percentage > 0:
            progress_bar = ctk.CTkFrame(
                progress_frame,
                fg_color=COLORS["primary"],
                height=25,
                corner_radius=5,
                width=int(progress_frame.winfo_width() * percentage / 100)
            )
            progress_bar.place(relwidth=percentage/100, relheight=1)
        
        # Quantidade
        quantity_label = ctk.CTkLabel(
            row,
            text=f"{quantity} ({percentage:.1f}%)",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["primary"]
        )
        quantity_label.pack(side="right", padx=(20, 0))
    
    def load_data(self):
        """Carrega dados do dashboard"""
        # Obter filial do usuário
        branch_id = None if auth_manager.can_view_all_branches() else auth_manager.get_user_branch()
        
        # Usar banco de dados
        stats = BrindeDAO.get_stats(branch_id)
        category_stats = BrindeDAO.get_by_category_stats(branch_id)
        
        # Atualizar cards
        self.total_items_card["value"].configure(text=str(stats.get("total_itens", 0) or 0))
        self.total_products_card["value"].configure(text=str(stats.get("total_produtos", 0) or 0))
        self.total_value_card["value"].configure(text=f"R$ {stats.get('valor_total', 0) or 0:,.2f}")
        self.low_stock_card["value"].configure(text=str(stats.get("itens_estoque_baixo", 0) or 0))
        
        # Limpar container de categorias
        for widget in self.categories_container.winfo_children():
            widget.destroy()
        
        # Calcular total para percentuais
        total = stats.get("total_itens", 0) or 0
        
        # Criar linhas de categoria
        if total > 0 and category_stats:
            for cat_stat in category_stats:
                quantity = cat_stat["total_itens"]
                percentage = (quantity / total) * 100
                self._create_category_row(
                    self.categories_container,
                    cat_stat["categoria"],
                    quantity,
                    percentage
                )
        else:
            no_data_label = ctk.CTkLabel(
                self.categories_container,
                text="Nenhum item em estoque",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data_label.pack(pady=50)
