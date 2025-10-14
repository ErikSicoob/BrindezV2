# -*- coding: utf-8 -*-
"""
Tela de Relatórios
"""
import customtkinter as ctk
from ui.components.form_dialog import show_info, show_error, FormDialog, ConfirmDialog
from config.settings import COLORS
from utils.report_generator import report_generator
from database.dao import BrindeDAO, BrindeExcluidoDAO
from datetime import datetime, timedelta


class RelatoriosView(ctk.CTkFrame):
    """View de relatórios"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLORS["content_bg"])
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets da tela"""
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_container,
            text="📈 Relatórios Disponíveis",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["dark"]
        )
        title.pack(pady=(0, 30))
        
        # Grid de relatórios
        reports_grid = ctk.CTkFrame(main_container, fg_color="transparent")
        reports_grid.pack(fill="both", expand=True)
        
        # Configurar grid
        reports_grid.grid_columnconfigure(0, weight=1)
        reports_grid.grid_columnconfigure(1, weight=1)
        
        # Relatórios
        reports = [
            ("📦 Estoque Atual", "Relatório completo de estoque por filial", 0, 0),
            ("🔄 Movimentações", "Histórico de movimentações por período", 0, 1),
            ("➡️ Transferências", "Transferências entre filiais", 1, 0),
            ("⚠️ Estoque Baixo", "Itens com estoque abaixo do mínimo", 1, 1),
            ("💰 Valor por Categoria", "Valor total de estoque por categoria", 2, 0),
            ("👥 Usuários", "Relatório de usuários ativos/inativos", 2, 1),
            ("📜 Histórico de Item", "Histórico completo de movimentações", 3, 0),
            ("🗑️ Brindes Excluídos", "Auditoria de brindes excluídos do sistema", 3, 1),
        ]
        
        for title, desc, row, col in reports:
            self._create_report_card(reports_grid, title, desc, row, col)
    
    def _create_report_card(self, parent, title, description, row, col):
        """Cria um card de relatório"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configurar hover
        card.bind("<Enter>", lambda e: card.configure(fg_color="#f0f0f0"))
        card.bind("<Leave>", lambda e: card.configure(fg_color="white"))
        card.bind("<Button-1>", lambda e: self.generate_report(title))
        
        # Título
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["dark"]
        )
        title_label.pack(padx=20, pady=(20, 10), anchor="w")
        title_label.bind("<Button-1>", lambda e: self.generate_report(title))
        
        # Descrição
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=("Segoe UI", 11),
            text_color="#666666",
            wraplength=250
        )
        desc_label.pack(padx=20, pady=(0, 15), anchor="w")
        desc_label.bind("<Button-1>", lambda e: self.generate_report(title))
        
        # Botão
        button = ctk.CTkButton(
            card,
            text="Gerar Relatório",
            font=("Segoe UI", 12),
            height=35,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            command=lambda: self.generate_report(title)
        )
        button.pack(padx=20, pady=(0, 20), fill="x")
    
    def generate_report(self, report_name):
        """Gera relatório"""
        if report_name == "📦 Estoque Atual":
            self.show_estoque_atual()
        elif report_name == "🔄 Movimentações":
            self.show_movimentacoes()
        elif report_name == "➡️ Transferências":
            self.show_transferencias()
        elif report_name == "⚠️ Estoque Baixo":
            self.show_estoque_baixo()
        elif report_name == "💰 Valor por Categoria":
            self.show_valor_categoria()
        elif report_name == "👥 Usuários":
            self.show_usuarios()
        elif report_name == "📜 Histórico de Item":
            self.show_historico_item()
        elif report_name == "🗑️ Brindes Excluídos":
            self.show_brindes_excluidos()
        else:
            show_info("Em Desenvolvimento", f"Geração do relatório '{report_name}' será implementada em breve!")
    
    def show_brindes_excluidos(self):
        """Mostra relatório de brindes excluídos"""
        
        # Dialog para o relatório
        dialog = FormDialog(self, "🗑️ Relatório de Brindes Excluídos", width=1000, height=600)
        
        # Frame para filtros
        filter_frame = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Botão para atualizar
        refresh_btn = ctk.CTkButton(
            filter_frame,
            text="🔄 Atualizar",
            width=100,
            command=lambda: self.load_brindes_excluidos(list_frame)
        )
        refresh_btn.pack(side="right")
        
        # Frame para lista
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True)
        
        # Carregar dados
        self.load_brindes_excluidos(list_frame)
        
        # Botão fechar
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def load_brindes_excluidos(self, list_frame):
        """Carrega lista de brindes excluídos"""
        
        # Limpar lista atual
        for widget in list_frame.winfo_children():
            widget.destroy()
        
        # Buscar dados
        brindes_excluidos = BrindeExcluidoDAO.get_all(limit=50)
        
        if not brindes_excluidos:
            no_data = ctk.CTkLabel(
                list_frame,
                text="Nenhum brinde excluído encontrado",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data.pack(pady=50)
            return
        
        # Cabeçalho
        header = ctk.CTkFrame(list_frame, fg_color="#e3f2fd", corner_radius=5)
        header.pack(fill="x", padx=5, pady=(5, 10))
        
        headers = ["Descrição", "Categoria", "Qtd", "Valor", "Excluído em", "Por", "Motivo"]
        for i, text in enumerate(headers):
            label = ctk.CTkLabel(header, text=text, font=("Segoe UI", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Dados
        for brinde in brindes_excluidos:
            row = ctk.CTkFrame(list_frame, fg_color="#f8f9fa", corner_radius=3)
            row.pack(fill="x", padx=5, pady=2)
            
            # Formatar data
            try:
                data_exclusao = datetime.fromisoformat(brinde["data_exclusao"].replace("Z", "+00:00"))
                data_str = data_exclusao.strftime("%d/%m/%Y %H:%M")
            except:
                data_str = brinde["data_exclusao"]
            
            # Dados da linha
            dados = [
                brinde["descricao"][:30] + "..." if len(brinde["descricao"]) > 30 else brinde["descricao"],
                brinde["categoria_nome"] or "-",
                str(brinde["quantidade"] or 0),
                f"R$ {brinde['valor_unitario']:.2f}" if brinde["valor_unitario"] else "R$ 0,00",
                data_str,
                brinde["usuario_exclusao_nome"],
                brinde["motivo_exclusao"][:20] + "..." if brinde["motivo_exclusao"] and len(brinde["motivo_exclusao"]) > 20 else (brinde["motivo_exclusao"] or "-")
            ]
            
            for i, text in enumerate(dados):
                label = ctk.CTkLabel(row, text=text, font=("Segoe UI", 10))
                label.grid(row=0, column=i, padx=8, pady=8, sticky="w")
    
    def show_estoque_atual(self):
        """Relatório de estoque atual"""
        
        dialog = FormDialog(self, "📦 Relatório de Estoque Atual", width=1200, height=600)
        
        # Frame para lista
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Buscar dados
        dados = report_generator.get_estoque_atual()
        
        if not dados:
            no_data = ctk.CTkLabel(list_frame, text="Nenhum item encontrado", font=("Segoe UI", 14), text_color="#999999")
            no_data.pack(pady=50)
        else:
            self._create_table(list_frame, dados, [
                ("Descrição", "descricao"),
                ("Categoria", "categoria"),
                ("Qtd", "quantidade"),
                ("Unidade", "unidade"),
                ("Valor Unit.", "valor_unitario"),
                ("Valor Total", "valor_total"),
                ("Filial", "filial"),
                ("Status", "status_estoque")
            ])
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def show_movimentacoes(self):
        """Relatório de movimentações"""
        from ui.components.form_dialog import FormDialog
        from utils.report_generator import report_generator
        import customtkinter as ctk
        from datetime import datetime, timedelta
        
        dialog = FormDialog(self, "🔄 Relatório de Movimentações", width=1200, height=600)
        
        # Filtros de data
        filter_frame = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        # Data início
        start_label = ctk.CTkLabel(filter_frame, text="Data Início:")
        start_label.pack(side="left", padx=(0, 5))
        
        start_entry = ctk.CTkEntry(filter_frame, width=100)
        start_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        start_entry.pack(side="left", padx=(0, 10))
        
        # Data fim
        end_label = ctk.CTkLabel(filter_frame, text="Data Fim:")
        end_label.pack(side="left", padx=(0, 5))
        
        end_entry = ctk.CTkEntry(filter_frame, width=100)
        end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        end_entry.pack(side="left", padx=(0, 10))
        
        # Botão filtrar
        filter_btn = ctk.CTkButton(filter_frame, text="🔍 Filtrar", width=80,
                                   command=lambda: self._load_movimentacoes(list_frame, start_entry.get(), end_entry.get()))
        filter_btn.pack(side="left", padx=10)
        
        # Frame para lista
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        # Carregar dados iniciais
        self._load_movimentacoes(list_frame, start_entry.get(), end_entry.get())
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def _load_movimentacoes(self, list_frame, data_inicio, data_fim):
        """Carrega movimentações"""
        from utils.report_generator import report_generator
        
        # Limpar lista
        for widget in list_frame.winfo_children():
            widget.destroy()
        
        dados = report_generator.get_movimentacoes(data_inicio, data_fim)
        
        if not dados:
            no_data = ctk.CTkLabel(list_frame, text="Nenhuma movimentação encontrada", font=("Segoe UI", 14), text_color="#999999")
            no_data.pack(pady=50)
        else:
            self._create_table(list_frame, dados, [
                ("Data", "data_movimentacao"),
                ("Tipo", "tipo"),
                ("Brinde", "brinde"),
                ("Qtd", "quantidade"),
                ("Valor Unit.", "valor_unitario"),
                ("Valor Total", "valor_total"),
                ("Usuário", "usuario"),
                ("Filial", "filial")
            ])
    
    def show_estoque_baixo(self):
        """Relatório de estoque baixo"""
        from ui.components.form_dialog import FormDialog
        from utils.report_generator import report_generator
        import customtkinter as ctk
        
        dialog = FormDialog(self, "⚠️ Relatório de Estoque Baixo", width=1000, height=600)
        
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        dados = report_generator.get_estoque_baixo()
        
        if not dados:
            no_data = ctk.CTkLabel(list_frame, text="✅ Nenhum item com estoque baixo!", font=("Segoe UI", 14), text_color=COLORS["success"])
            no_data.pack(pady=50)
        else:
            self._create_table(list_frame, dados, [
                ("Descrição", "descricao"),
                ("Categoria", "categoria"),
                ("Qtd Atual", "quantidade"),
                ("Qtd Mínima", "estoque_minimo"),
                ("Unidade", "unidade"),
                ("Filial", "filial"),
                ("Fornecedor", "fornecedor")
            ])
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def show_valor_categoria(self):
        """Relatório de valor por categoria"""
        from ui.components.form_dialog import FormDialog
        from utils.report_generator import report_generator
        import customtkinter as ctk
        
        dialog = FormDialog(self, "💰 Relatório de Valor por Categoria", width=1000, height=600)
        
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        dados = report_generator.get_valor_por_categoria()
        
        if not dados:
            no_data = ctk.CTkLabel(list_frame, text="Nenhum dado encontrado", font=("Segoe UI", 14), text_color="#999999")
            no_data.pack(pady=50)
        else:
            self._create_table(list_frame, dados, [
                ("Categoria", "categoria"),
                ("Total Itens", "total_itens"),
                ("Qtd Total", "quantidade_total"),
                ("Valor Total", "valor_total"),
                ("Valor Médio", "valor_medio"),
                ("Filial", "filial")
            ])
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def show_usuarios(self):
        """Relatório de usuários"""
        from ui.components.form_dialog import FormDialog
        from utils.report_generator import report_generator
        import customtkinter as ctk
        
        dialog = FormDialog(self, "👥 Relatório de Usuários", width=1200, height=600)
        
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        dados = report_generator.get_usuarios_report()
        
        if not dados:
            no_data = ctk.CTkLabel(list_frame, text="Nenhum usuário encontrado", font=("Segoe UI", 14), text_color="#999999")
            no_data.pack(pady=50)
        else:
            self._create_table(list_frame, dados, [
                ("Nome", "nome"),
                ("Username", "username"),
                ("Email", "email"),
                ("Perfil", "perfil"),
                ("Filial", "filial"),
                ("Status", "status"),
                ("Movimentações", "total_movimentacoes")
            ])
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def show_transferencias(self):
        """Relatório de transferências"""
        from ui.components.form_dialog import FormDialog
        from utils.report_generator import report_generator
        import customtkinter as ctk
        from datetime import datetime, timedelta
        
        dialog = FormDialog(self, "➡️ Relatório de Transferências", width=1200, height=600)
        
        # Filtros de data
        filter_frame = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 10))
        
        start_label = ctk.CTkLabel(filter_frame, text="Data Início:")
        start_label.pack(side="left", padx=(0, 5))
        
        start_entry = ctk.CTkEntry(filter_frame, width=100)
        start_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
        start_entry.pack(side="left", padx=(0, 10))
        
        end_label = ctk.CTkLabel(filter_frame, text="Data Fim:")
        end_label.pack(side="left", padx=(0, 5))
        
        end_entry = ctk.CTkEntry(filter_frame, width=100)
        end_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        end_entry.pack(side="left", padx=(0, 10))
        
        filter_btn = ctk.CTkButton(filter_frame, text="🔍 Filtrar", width=80,
                                   command=lambda: self._load_transferencias(list_frame, start_entry.get(), end_entry.get()))
        filter_btn.pack(side="left", padx=10)
        
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        self._load_transferencias(list_frame, start_entry.get(), end_entry.get())
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def _load_transferencias(self, list_frame, data_inicio, data_fim):
        """Carrega transferências"""
        from utils.report_generator import report_generator
        
        for widget in list_frame.winfo_children():
            widget.destroy()
        
        dados = report_generator.get_transferencias(data_inicio, data_fim)
        
        if not dados:
            no_data = ctk.CTkLabel(list_frame, text="Nenhuma transferência encontrada", font=("Segoe UI", 14), text_color="#999999")
            no_data.pack(pady=50)
        else:
            self._create_table(list_frame, dados, [
                ("Data", "data_transferencia"),
                ("Brinde", "brinde"),
                ("Quantidade", "quantidade"),
                ("Origem", "filial_origem"),
                ("Destino", "filial_destino"),
                ("Usuário", "usuario"),
                ("Justificativa", "justificativa")
            ])
    
    def show_historico_item(self):
        """Relatório de histórico de item"""
        from ui.components.form_dialog import FormDialog, show_error
        from database.dao import BrindeDAO
        import customtkinter as ctk
        
        # Dialog para selecionar item
        dialog = FormDialog(self, "📜 Histórico de Item - Selecionar", width=600, height=400)
        
        # Buscar brindes
        brindes = BrindeDAO.get_all()
        if not brindes:
            show_error("Erro", "Nenhum brinde cadastrado!")
            dialog.safe_destroy()
            return
        
        # Combo de seleção
        brinde_combo = dialog.add_field("Selecione o Brinde", "combobox",
                                        values=[f"{b['descricao']} - {b['filial']}" for b in brindes])
        
        def show_historico():
            selected = brinde_combo.get()
            if not selected:
                show_error("Erro", "Selecione um brinde!")
                return
            
            # Encontrar brinde selecionado
            brinde_selecionado = None
            for b in brindes:
                if f"{b['descricao']} - {b['filial']}" == selected:
                    brinde_selecionado = b
                    break
            
            if brinde_selecionado:
                dialog.safe_destroy()
                self._show_historico_detalhado(brinde_selecionado["id"])
        
        dialog.add_buttons(show_historico)
    
    def _show_historico_detalhado(self, brinde_id):
        """Mostra histórico detalhado do item"""
        from ui.components.form_dialog import FormDialog
        from utils.report_generator import report_generator
        import customtkinter as ctk
        from datetime import datetime
        
        # Buscar dados
        dados = report_generator.get_historico_item(brinde_id)
        
        if not dados["brinde"]:
            show_error("Erro", "Brinde não encontrado!")
            return
        
        brinde = dados["brinde"]
        dialog = FormDialog(self, f"📜 Histórico: {brinde['descricao']}", width=1200, height=700)
        
        # Informações do brinde
        info_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#e3f2fd", corner_radius=8)
        info_frame.pack(fill="x", pady=(0, 10))
        
        info_text = f"📦 {brinde['descricao']} | 🏷️ {brinde['categoria']} | 📍 {brinde['filial']} | 📊 Qtd: {brinde['quantidade']} {brinde['unidade']}"
        info_label = ctk.CTkLabel(info_frame, text=info_text, font=("Segoe UI", 12, "bold"))
        info_label.pack(pady=10)
        
        # Abas para movimentações e transferências
        tabview = ctk.CTkTabview(dialog.content_frame)
        tabview.pack(fill="both", expand=True)
        
        # Aba movimentações
        tabview.add("Movimentações")
        mov_frame = ctk.CTkScrollableFrame(tabview.tab("Movimentações"), fg_color="white")
        mov_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        if dados["movimentacoes"]:
            self._create_table(mov_frame, dados["movimentacoes"], [
                ("Data", "data_movimentacao"),
                ("Tipo", "tipo"),
                ("Quantidade", "quantidade"),
                ("Valor Unit.", "valor_unitario"),
                ("Usuário", "usuario"),
                ("Justificativa", "justificativa")
            ])
        else:
            no_mov = ctk.CTkLabel(mov_frame, text="Nenhuma movimentação encontrada", font=("Segoe UI", 12), text_color="#999999")
            no_mov.pack(pady=20)
        
        # Aba transferências
        tabview.add("Transferências")
        trans_frame = ctk.CTkScrollableFrame(tabview.tab("Transferências"), fg_color="white")
        trans_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        if dados["transferencias"]:
            self._create_table(trans_frame, dados["transferencias"], [
                ("Data", "data_transferencia"),
                ("Quantidade", "quantidade"),
                ("Origem", "filial_origem"),
                ("Destino", "filial_destino"),
                ("Usuário", "usuario"),
                ("Justificativa", "justificativa")
            ])
        else:
            no_trans = ctk.CTkLabel(trans_frame, text="Nenhuma transferência encontrada", font=("Segoe UI", 12), text_color="#999999")
            no_trans.pack(pady=20)
        
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def _create_table(self, parent, dados, colunas):
        """Cria uma tabela genérica"""
        import customtkinter as ctk
        from datetime import datetime
        
        # Cabeçalho
        header = ctk.CTkFrame(parent, fg_color="#e3f2fd", corner_radius=5)
        header.pack(fill="x", padx=5, pady=(5, 10))
        
        for i, (titulo, _) in enumerate(colunas):
            label = ctk.CTkLabel(header, text=titulo, font=("Segoe UI", 12, "bold"))
            label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
        
        # Dados
        for item in dados:
            row = ctk.CTkFrame(parent, fg_color="#f8f9fa", corner_radius=3)
            row.pack(fill="x", padx=5, pady=2)
            
            for i, (_, campo) in enumerate(colunas):
                valor = item.get(campo, "")
                
                # Formatação especial para alguns campos
                if campo in ["valor_unitario", "valor_total", "valor_medio"] and valor:
                    texto = f"R$ {float(valor):.2f}"
                elif campo in ["data_movimentacao", "data_transferencia", "data_criacao"] and valor:
                    try:
                        if isinstance(valor, str):
                            dt = datetime.fromisoformat(valor.replace("Z", "+00:00"))
                        else:
                            dt = valor
                        texto = dt.strftime("%d/%m/%Y %H:%M")
                    except:
                        texto = str(valor)
                elif campo == "tipo" and valor:
                    texto = "📈 ENTRADA" if valor == "ENTRADA" else "📉 SAÍDA"
                elif campo == "status_estoque" and valor:
                    texto = "⚠️ BAIXO" if valor == "BAIXO" else "✅ OK"
                else:
                    texto = str(valor) if valor is not None else "-"
                
                # Truncar texto longo
                if len(texto) > 30:
                    texto = texto[:27] + "..."
                
                label = ctk.CTkLabel(row, text=texto, font=("Segoe UI", 10))
                label.grid(row=0, column=i, padx=8, pady=8, sticky="w")
