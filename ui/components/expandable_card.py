# -*- coding: utf-8 -*-
"""
Componente de Card Expandível
Para mostrar informações detalhadas por filial
"""
import customtkinter as ctk
from config.settings import COLORS
from ui.components.context_menu import show_context_menu


class ExpandableCard(ctk.CTkFrame):
    """Card com expansão para mostrar detalhes"""
    
    def __init__(self, master, title, data, on_edit=None, on_add_stock=None, on_remove_stock=None, on_transfer=None, on_delete=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="white", corner_radius=5)
        self.data = data
        self.on_edit = on_edit
        self.on_add_stock = on_add_stock
        self.on_remove_stock = on_remove_stock
        self.on_transfer = on_transfer
        self.on_delete = on_delete
        self.expanded = False
        
        self._create_header(title)
        self._create_details_frame()
    
    def _create_header(self, title):
        """Cria cabeçalho do card"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", cursor="hand2")
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.bind("<Button-1>", lambda e: self.toggle_expansion())
        
        # Botão de expansão
        self.expand_btn = ctk.CTkLabel(
            header_frame,
            text="▶",
            font=("Segoe UI", 14, "bold"),
            text_color=COLORS["primary"],
            cursor="hand2",
            width=30
        )
        self.expand_btn.pack(side="left", padx=(0, 10))
        self.expand_btn.bind("<Button-1>", lambda e: self.toggle_expansion())
        
        # Título e informações principais
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)
        info_frame.bind("<Button-1>", lambda e: self.toggle_expansion())
        
        title_label = ctk.CTkLabel(
            info_frame,
            text=title,
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["dark"],
            anchor="w"
        )
        title_label.pack(side="left", padx=(0, 20))
        title_label.bind("<Button-1>", lambda e: self.toggle_expansion())
        
        # Resumo das quantidades
        summary = self._create_summary()
        summary_label = ctk.CTkLabel(
            info_frame,
            text=summary,
            font=("Segoe UI", 11),
            text_color="#666666",
            anchor="w"
        )
        summary_label.pack(side="left")
        summary_label.bind("<Button-1>", lambda e: self.toggle_expansion())
    
    def _create_summary(self):
        """Cria resumo das informações"""
        if not self.data:
            return "Sem dados"
        
        total_qty = sum(item.get('quantidade', 0) for item in self.data)
        total_value = sum(item.get('quantidade', 0) * item.get('valor_unitario', 0) for item in self.data)
        num_filiais = len(self.data)
        
        return f"📦 {total_qty} un • 💰 R$ {total_value:,.2f} • 🏢 {num_filiais} filiai{'s' if num_filiais != 1 else ''}"
    
    def _create_details_frame(self):
        """Cria frame de detalhes (inicialmente oculto)"""
        self.details_frame = ctk.CTkFrame(self, fg_color="#f8f9fa", corner_radius=5)
        
        if not self.data:
            no_data_label = ctk.CTkLabel(
                self.details_frame,
                text="Nenhum dado disponível",
                font=("Segoe UI", 11),
                text_color="#999999"
            )
            no_data_label.pack(pady=20)
            return
        
        # Cabeçalho da tabela
        header = ctk.CTkFrame(self.details_frame, fg_color=COLORS["info"], corner_radius=0)
        header.pack(fill="x", pady=(10, 0), padx=10)
        
        headers = ["Filial", "Quantidade", "Valor Unit.", "Valor Total", "Categoria", "Fornecedor"]
        for i, text in enumerate(headers):
            label = ctk.CTkLabel(
                header,
                text=text,
                font=("Segoe UI", 10, "bold"),
                text_color="white"
            )
            label.grid(row=0, column=i, padx=8, pady=8, sticky="w")
        
        # Linhas de dados
        data_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        data_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        for idx, item in enumerate(self.data):
            row_frame = ctk.CTkFrame(
                data_frame,
                fg_color="white" if idx % 2 == 0 else "#f0f0f0",
                corner_radius=3
            )
            row_frame.pack(fill="x", pady=2)
            
            # Filial
            filial_text = f"{item.get('filial_numero', '')} - {item.get('filial', 'N/A')}"
            filial_label = ctk.CTkLabel(
                row_frame,
                text=filial_text,
                font=("Segoe UI", 10),
                anchor="w",
                width=150
            )
            filial_label.grid(row=0, column=0, padx=8, pady=5, sticky="w")
            
            # Quantidade
            qty_label = ctk.CTkLabel(
                row_frame,
                text=f"{item.get('quantidade', 0)} {item.get('unidade', '')}",
                font=("Segoe UI", 10),
                anchor="w",
                width=100
            )
            qty_label.grid(row=0, column=1, padx=8, pady=5, sticky="w")
            
            # Valor Unitário
            valor_unit = item.get('valor_unitario', 0)
            valor_label = ctk.CTkLabel(
                row_frame,
                text=f"R$ {valor_unit:,.2f}",
                font=("Segoe UI", 10),
                anchor="w",
                width=100
            )
            valor_label.grid(row=0, column=2, padx=8, pady=5, sticky="w")
            
            # Valor Total
            valor_total = item.get('quantidade', 0) * valor_unit
            total_label = ctk.CTkLabel(
                row_frame,
                text=f"R$ {valor_total:,.2f}",
                font=("Segoe UI", 10, "bold"),
                anchor="w",
                width=100,
                text_color=COLORS["success"]
            )
            total_label.grid(row=0, column=3, padx=8, pady=5, sticky="w")
            
            # Categoria
            cat_label = ctk.CTkLabel(
                row_frame,
                text=item.get('categoria', 'N/A'),
                font=("Segoe UI", 10),
                anchor="w",
                width=120
            )
            cat_label.grid(row=0, column=4, padx=8, pady=5, sticky="w")
            
            # Fornecedor
            forn_label = ctk.CTkLabel(
                row_frame,
                text=item.get('fornecedor', '-'),
                font=("Segoe UI", 10),
                anchor="w",
                width=120
            )
            forn_label.grid(row=0, column=5, padx=8, pady=5, sticky="w")
            
            # Bind menu de contexto para a linha
            self._bind_context_menu(row_frame, item)
    
    def _bind_context_menu(self, widget, item):
        """Vincula menu de contexto ao widget"""
        def show_menu(event):
            menu_items = []
            
            # Editar
            if self.on_edit:
                menu_items.append({
                    'label': '✏️ Editar',
                    'command': lambda: self.on_edit(item)
                })
            
            # Entrada
            if self.on_add_stock:
                menu_items.append({
                    'label': '📥 Entrada de Estoque',
                    'command': lambda: self.on_add_stock(item),
                    'color': COLORS["success"]
                })
            
            # Saída
            if self.on_remove_stock:
                menu_items.append({
                    'label': '📤 Saída de Estoque',
                    'command': lambda: self.on_remove_stock(item),
                    'color': COLORS["warning"]
                })
            
            # Transferir
            if self.on_transfer:
                menu_items.append({
                    'label': '🔄 Transferir para Filial',
                    'command': lambda: self.on_transfer(item),
                    'color': COLORS["info"]
                })
            
            # Separador
            if menu_items and self.on_delete:
                menu_items.append({'separator': True})
            
            # Excluir
            if self.on_delete:
                menu_items.append({
                    'label': '🗑️ Excluir',
                    'command': lambda: self.on_delete(item),
                    'color': COLORS["danger"]
                })
            
            if menu_items:
                show_context_menu(widget, event, menu_items)
        
        widget.bind("<Button-3>", show_menu)
        
        # Bind também para todos os widgets filhos
        for child in widget.winfo_children():
            child.bind("<Button-3>", show_menu)
    
    def toggle_expansion(self):
        """Alterna entre expandido e recolhido"""
        self.expanded = not self.expanded
        
        if self.expanded:
            self.expand_btn.configure(text="▼")
            self.details_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        else:
            self.expand_btn.configure(text="▶")
            self.details_frame.pack_forget()
