# -*- coding: utf-8 -*-
"""
Tela de Gestão de Brindes - Versão Completa com BD
"""
import customtkinter as ctk
from config.settings import COLORS
from database.dao import BrindeDAO, CategoriaDAO, UnidadeDAO, FilialDAO, FornecedorDAO, MovimentacaoDAO, BrindeExcluidoDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from utils.event_manager import event_manager, EVENTS
from utils.auth import auth_manager


class BrindesView(ctk.CTkFrame):
    """View de gestão de brindes"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLORS["content_bg"])
        self.current_page = 0
        self.items_per_page = 20
        self.selected_brinde = None
        
        # Filtros
        self.filters = {
            "categoria": None,
            "filial": None,
            "fornecedor": None,
            "valor_min": None,
            "valor_max": None,
            "qtd_min": None,
            "qtd_max": None,
            "data_inicio": None,
            "data_fim": None
        }
        
        self._create_widgets()
        self.load_brindes()
        
        # Inscrever para eventos com verificação de segurança
        event_manager.subscribe(EVENTS['BRINDE_CREATED'], lambda d: self._safe_reload())
        event_manager.subscribe(EVENTS['BRINDE_UPDATED'], lambda d: self._safe_reload())
        event_manager.subscribe(EVENTS['BRINDE_DELETED'], lambda d: self._safe_reload())
        event_manager.subscribe(EVENTS['STOCK_CHANGED'], lambda d: self._safe_reload())
        event_manager.subscribe(EVENTS['CATEGORIA_CHANGED'], lambda d: self._safe_reload())
        event_manager.subscribe(EVENTS['UNIDADE_CHANGED'], lambda d: self._safe_reload())
        event_manager.subscribe(EVENTS['FORNECEDOR_CHANGED'], lambda d: self._safe_reload())
    
    def _safe_reload(self):
        """Recarrega a lista de forma segura, verificando se a view ainda existe"""
        try:
            if hasattr(self, 'winfo_exists') and self.winfo_exists():
                self.load_brindes()
        except Exception as e:
            from utils.logger import logger
            logger.debug(f"View não existe mais durante _safe_reload: {e}")
    
    def _create_widgets(self):
        """Cria os widgets da tela"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Barra de ações
        actions_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, 20))
        
        new_button = ctk.CTkButton(
            actions_frame,
            text="➕ Novo Brinde",
            font=("Segoe UI", 14, "bold"),
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_dark"],
            command=self.show_new_brinde_form
        )
        new_button.pack(side="left", padx=5)
        
        # Botão de filtros
        filter_button = ctk.CTkButton(
            actions_frame,
            text="🔍 Filtros",
            font=("Segoe UI", 12),
            height=40,
            width=120,
            corner_radius=8,
            fg_color=COLORS["secondary"],
            hover_color="#5a6268",
            command=self.show_filters_dialog
        )
        filter_button.pack(side="left", padx=5)
        
        # Botão limpar filtros
        clear_button = ctk.CTkButton(
            actions_frame,
            text="✖ Limpar",
            font=("Segoe UI", 12),
            height=40,
            width=100,
            corner_radius=8,
            fg_color="#dc3545",
            hover_color="#c82333",
            command=self.clear_filters
        )
        clear_button.pack(side="left", padx=5)
        
        # Label de filtros ativos
        self.active_filters_label = ctk.CTkLabel(
            actions_frame,
            text="",
            font=("Segoe UI", 11),
            text_color=COLORS["primary"]
        )
        self.active_filters_label.pack(side="left", padx=10)
        
        items_label = ctk.CTkLabel(actions_frame, text="Itens/página:", font=("Segoe UI", 12))
        items_label.pack(side="right", padx=(20, 5))
        
        self.items_per_page_combo = ctk.CTkComboBox(
            actions_frame,
            values=["10", "20", "50", "100"],
            width=100,
            command=self._on_items_per_page_change
        )
        self.items_per_page_combo.pack(side="right", padx=5)
        self.items_per_page_combo.set("20")
        
        # Container de lista
        list_container = ctk.CTkFrame(main_container, fg_color="white", corner_radius=10)
        list_container.pack(fill="both", expand=True)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(list_container, fg_color=COLORS["primary"], corner_radius=0)
        header_frame.pack(fill="x")
        
        headers = ["Descrição", "Categoria", "Qtd", "Un", "Valor Unit.", "Valor Total", "Filial", "Ações"]
        for text in headers:
            label = ctk.CTkLabel(header_frame, text=text, font=("Segoe UI", 12, "bold"), text_color="white")
            label.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        # Lista
        self.list_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent", corner_radius=0)
        self.list_frame.pack(fill="both", expand=True)
        
        # Paginação
        pagination_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        pagination_frame.pack(fill="x", padx=20, pady=10)
        
        self.prev_button = ctk.CTkButton(pagination_frame, text="◀ Anterior", width=100, command=self.prev_page)
        self.prev_button.pack(side="left")
        
        self.page_label = ctk.CTkLabel(pagination_frame, text="Página 1 de 1", font=("Segoe UI", 12))
        self.page_label.pack(side="left", expand=True)
        
        self.next_button = ctk.CTkButton(pagination_frame, text="Próxima ▶", width=100, command=self.next_page)
        self.next_button.pack(side="right")
    
    def _on_items_per_page_change(self, value):
        """Handler de mudança de itens por página"""
        self.items_per_page = int(value)
        self.current_page = 0
        self._safe_reload()
    
    def _create_brinde_row(self, brinde):
        """Cria uma linha de brinde"""
        row = ctk.CTkFrame(self.list_frame, fg_color="#f8f9fa", corner_radius=5, height=50)
        row.pack(fill="x", padx=5, pady=3)
        
        # Dados
        desc_label = ctk.CTkLabel(row, text=brinde["descricao"], font=("Segoe UI", 11))
        desc_label.pack(side="left", padx=10, fill="x", expand=True)
        
        cat_label = ctk.CTkLabel(row, text=brinde["categoria"], font=("Segoe UI", 11))
        cat_label.pack(side="left", padx=10, fill="x", expand=True)
        
        qtd_label = ctk.CTkLabel(row, text=str(brinde["quantidade"]), font=("Segoe UI", 11))
        qtd_label.pack(side="left", padx=10, fill="x", expand=True)
        
        un_label = ctk.CTkLabel(row, text=brinde["unidade"], font=("Segoe UI", 11))
        un_label.pack(side="left", padx=10, fill="x", expand=True)
        
        val_label = ctk.CTkLabel(row, text=f"R$ {brinde['valor_unitario']:.2f}", font=("Segoe UI", 11))
        val_label.pack(side="left", padx=10, fill="x", expand=True)
        
        total_label = ctk.CTkLabel(row, text=f"R$ {brinde['valor_total']:.2f}", font=("Segoe UI", 11))
        total_label.pack(side="left", padx=10, fill="x", expand=True)
        
        fil_label = ctk.CTkLabel(row, text=brinde["filial"], font=("Segoe UI", 11))
        fil_label.pack(side="left", padx=10, fill="x", expand=True)
        
        # Botões de ação
        actions_frame = ctk.CTkFrame(row, fg_color="transparent")
        actions_frame.pack(side="left", padx=10)
        
        edit_btn = ctk.CTkButton(actions_frame, text="✏️", width=30, height=30, 
                                 command=lambda: self.edit_brinde(brinde))
        edit_btn.pack(side="left", padx=2)
        
        entrada_btn = ctk.CTkButton(actions_frame, text="📥", width=30, height=30,
                                     fg_color=COLORS["success"],
                                     command=lambda: self.add_stock(brinde))
        entrada_btn.pack(side="left", padx=2)
        
        saida_btn = ctk.CTkButton(actions_frame, text="📤", width=30, height=30,
                                  fg_color=COLORS["warning"],
                                  command=lambda: self.remove_stock(brinde))
        saida_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(actions_frame, text="🗑️", width=30, height=30,
                                    fg_color=COLORS["danger"],
                                    command=lambda: self.delete_brinde(brinde))
        delete_btn.pack(side="left", padx=2)
    
    def load_brindes(self):
        """Carrega lista de brindes com filtros aplicados"""
        # Verificar se a view ainda existe
        try:
            if not hasattr(self, 'list_frame') or not self.list_frame.winfo_exists():
                return
        except:
            return
            
        try:
            for widget in self.list_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            # Se houver erro ao acessar widgets, a view foi destruída
            from utils.logger import logger
            logger.debug(f"View destruída durante load_brindes: {e}")
            return
        
        branch_id = None if auth_manager.can_view_all_branches() else auth_manager.get_user_branch()
        all_brindes = BrindeDAO.get_all(branch_id)
        
        # Aplicar filtros
        filtered_brindes = self._apply_filters(all_brindes)
        
        # Paginação
        total_pages = (len(filtered_brindes) - 1) // self.items_per_page + 1 if filtered_brindes else 1
        start_idx = self.current_page * self.items_per_page
        end_idx = start_idx + self.items_per_page
        brindes = filtered_brindes[start_idx:end_idx]
        
        for brinde in brindes:
            self._create_brinde_row(brinde)
        
        self.page_label.configure(text=f"Página {self.current_page + 1} de {total_pages}")
        self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")
        
        if not brindes:
            no_data = ctk.CTkLabel(self.list_frame, text="Nenhum brinde encontrado", 
                                   font=("Segoe UI", 14), text_color="#999999")
            no_data.pack(pady=50)
    
    def _apply_filters(self, brindes):
        """Aplica todos os filtros ativos"""
        filtered = brindes
        
        # Filtro por categoria
        if self.filters["categoria"]:
            filtered = [b for b in filtered if b["categoria"] == self.filters["categoria"]]
        
        # Filtro por filial
        if self.filters["filial"]:
            filial_numero = self.filters["filial"].split(" - ")[0]
            filtered = [b for b in filtered if b["filial_numero"] == filial_numero]
        
        # Filtro por fornecedor
        if self.filters["fornecedor"]:
            filtered = [b for b in filtered if b.get("fornecedor") == self.filters["fornecedor"]]
        
        # Filtro por valor
        if self.filters["valor_min"] is not None:
            filtered = [b for b in filtered if b["valor_unitario"] >= self.filters["valor_min"]]
        
        if self.filters["valor_max"] is not None:
            filtered = [b for b in filtered if b["valor_unitario"] <= self.filters["valor_max"]]
        
        # Filtro por quantidade
        if self.filters["qtd_min"] is not None:
            filtered = [b for b in filtered if b["quantidade"] >= self.filters["qtd_min"]]
        
        if self.filters["qtd_max"] is not None:
            filtered = [b for b in filtered if b["quantidade"] <= self.filters["qtd_max"]]
        
        return filtered
    
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._safe_reload()
    
    def next_page(self):
        self.current_page += 1
        self._safe_reload()
    
    def show_new_brinde_form(self):
        """Mostra formulário de novo brinde"""
        # Buscar dados FRESCOS do banco
        categorias = CategoriaDAO.get_all()
        unidades = UnidadeDAO.get_all()
        filiais = FilialDAO.get_all()
        fornecedores = FornecedorDAO.get_all()
        
        # Validar se há dados necessários
        if not categorias:
            show_error("Erro", "Não há categorias cadastradas!\nCadastre pelo menos uma categoria antes de criar um brinde.")
            return
        
        if not unidades:
            show_error("Erro", "Não há unidades de medida cadastradas!\nCadastre pelo menos uma unidade antes de criar um brinde.")
            return
        
        if not filiais:
            show_error("Erro", "Não há filiais cadastradas!\nCadastre pelo menos uma filial antes de criar um brinde.")
            return
        
        dialog = FormDialog(self, "Novo Brinde", width=700, height=600)
        
        # Campos
        desc_entry = dialog.add_field("Descrição *")
        qtd_entry = dialog.add_field("Quantidade Inicial")
        qtd_entry.insert(0, "0")
        valor_entry = dialog.add_field("Valor Unitário *")
        
        cat_combo = dialog.add_field("Categoria *", "combobox", 
                                     values=[c["nome"] for c in categorias])
        cat_combo.set(categorias[0]["nome"])
        
        un_combo = dialog.add_field("Unidade de Medida *", "combobox",
                                    values=[f"{u['codigo']} - {u['nome']}" for u in unidades])
        un_combo.set(f"{unidades[0]['codigo']} - {unidades[0]['nome']}")
        
        fil_combo = dialog.add_field("Filial *", "combobox",
                                     values=[f"{f['numero']} - {f['nome']}" for f in filiais])
        fil_combo.set(f"{filiais[0]['numero']} - {filiais[0]['nome']}")
        
        forn_combo = dialog.add_field("Fornecedor", "combobox",
                                      values=["Nenhum"] + [f["nome"] for f in fornecedores])
        forn_combo.set("Nenhum")
        
        cod_entry = dialog.add_field("Código Interno")
        obs_text = dialog.add_field("Observações", "textbox")
        estoque_min_entry = dialog.add_field("Estoque Mínimo")
        estoque_min_entry.insert(0, "10")
        
        def save():
            # Validar
            if not desc_entry.get() or not valor_entry.get():
                show_error("Erro", "Preencha todos os campos obrigatórios!")
                return
            
            try:
                # Obter IDs
                cat_nome = cat_combo.get()
                categoria = next((c for c in categorias if c["nome"] == cat_nome), None)
                
                un_codigo = un_combo.get().split(" - ")[0]
                unidade = next((u for u in unidades if u["codigo"] == un_codigo), None)
                
                fil_numero = fil_combo.get().split(" - ")[0]
                filial = next((f for f in filiais if f["numero"] == fil_numero), None)
                
                forn_nome = forn_combo.get()
                fornecedor = next((f for f in fornecedores if f["nome"] == forn_nome), None) if forn_nome != "Nenhum" else None
                
                # Criar brinde
                data = {
                    "descricao": desc_entry.get(),
                    "quantidade": int(qtd_entry.get() or 0),
                    "valor_unitario": float(valor_entry.get()),
                    "categoria_id": categoria["id"],
                    "unidade_id": unidade["id"],
                    "filial_id": filial["id"],
                    "fornecedor_id": fornecedor["id"] if fornecedor else None,
                    "codigo_interno": cod_entry.get() or None,
                    "observacoes": obs_text.get("1.0", "end-1c") or None,
                    "estoque_minimo": int(estoque_min_entry.get() or 10)
                }
                
                BrindeDAO.create(data)
                event_manager.emit(EVENTS['BRINDE_CREATED'])
                event_manager.emit(EVENTS['STOCK_CHANGED'])
                
                dialog.safe_destroy()
                show_info("Sucesso", "Brinde cadastrado com sucesso!")
                
            except Exception as e:
                show_error("Erro", f"Erro ao cadastrar brinde: {str(e)}")
        
        dialog.add_buttons(save)
    
    def edit_brinde(self, brinde):
        """Edita brinde"""
        # Buscar brinde completo e dados FRESCOS do banco
        brinde_full = BrindeDAO.get_by_id(brinde["id"])
        categorias = CategoriaDAO.get_all()
        unidades = UnidadeDAO.get_all()
        fornecedores = FornecedorDAO.get_all()
        
        # Validar se há dados necessários
        if not categorias:
            show_error("Erro", "Não há categorias cadastradas!")
            return
        
        if not unidades:
            show_error("Erro", "Não há unidades de medida cadastradas!")
            return
        
        dialog = FormDialog(self, f"Editar: {brinde['descricao']}", width=700, height=600)
        
        # Campos
        desc_entry = dialog.add_field("Descrição *")
        desc_entry.insert(0, brinde_full["descricao"])
        
        valor_entry = dialog.add_field("Valor Unitário *")
        valor_entry.insert(0, str(brinde_full["valor_unitario"]))
        
        cat_combo = dialog.add_field("Categoria *", "combobox",
                                     values=[c["nome"] for c in categorias])
        cat_atual = next((c for c in categorias if c["id"] == brinde_full["categoria_id"]), None)
        if cat_atual:
            cat_combo.set(cat_atual["nome"])
        else:
            cat_combo.set(categorias[0]["nome"])
        
        un_combo = dialog.add_field("Unidade de Medida *", "combobox",
                                    values=[f"{u['codigo']} - {u['nome']}" for u in unidades])
        un_atual = next((u for u in unidades if u["id"] == brinde_full["unidade_id"]), None)
        if un_atual:
            un_combo.set(f"{un_atual['codigo']} - {un_atual['nome']}")
        else:
            un_combo.set(f"{unidades[0]['codigo']} - {unidades[0]['nome']}")
        
        forn_combo = dialog.add_field("Fornecedor", "combobox",
                                      values=["Nenhum"] + [f["nome"] for f in fornecedores])
        if brinde_full.get("fornecedor_id"):
            forn_atual = next((f for f in fornecedores if f["id"] == brinde_full["fornecedor_id"]), None)
            forn_combo.set(forn_atual["nome"] if forn_atual else "Nenhum")
        else:
            forn_combo.set("Nenhum")
        
        cod_entry = dialog.add_field("Código Interno")
        if brinde_full.get("codigo_interno"):
            cod_entry.insert(0, brinde_full["codigo_interno"])
        
        obs_text = dialog.add_field("Observações", "textbox")
        if brinde_full.get("observacoes"):
            obs_text.insert("1.0", brinde_full["observacoes"])
        
        estoque_min_entry = dialog.add_field("Estoque Mínimo")
        estoque_min_entry.insert(0, str(brinde_full.get("estoque_minimo", 10)))
        
        def save():
            try:
                # Obter IDs
                cat_nome = cat_combo.get()
                categoria = next((c for c in categorias if c["nome"] == cat_nome), None)
                
                un_codigo = un_combo.get().split(" - ")[0]
                unidade = next((u for u in unidades if u["codigo"] == un_codigo), None)
                
                forn_nome = forn_combo.get()
                fornecedor = next((f for f in fornecedores if f["nome"] == forn_nome), None) if forn_nome != "Nenhum" else None
                
                # Atualizar
                data = {
                    "descricao": desc_entry.get(),
                    "valor_unitario": float(valor_entry.get()),
                    "categoria_id": categoria["id"],
                    "unidade_id": unidade["id"],
                    "fornecedor_id": fornecedor["id"] if fornecedor else None,
                    "codigo_interno": cod_entry.get() or None,
                    "observacoes": obs_text.get("1.0", "end-1c") or None,
                    "estoque_minimo": int(estoque_min_entry.get() or 10)
                }
                
                BrindeDAO.update(brinde["id"], data)
                event_manager.emit(EVENTS['BRINDE_UPDATED'])
                
                dialog.safe_destroy()
                show_info("Sucesso", "Brinde atualizado com sucesso!")
                
            except Exception as e:
                show_error("Erro", f"Erro ao atualizar brinde: {str(e)}")
        
        dialog.add_buttons(save)
    
    def add_stock(self, brinde):
        """Adiciona estoque"""
        dialog = FormDialog(self, f"Entrada: {brinde['descricao']}", width=500, height=350)
        
        qtd_entry = dialog.add_field("Quantidade *")
        valor_entry = dialog.add_field("Valor Unitário")
        valor_entry.insert(0, str(brinde["valor_unitario"]))
        just_text = dialog.add_field("Justificativa", "textbox")
        
        def save():
            try:
                qtd = int(qtd_entry.get())
                valor = float(valor_entry.get())
                just = just_text.get("1.0", "end-1c")
                
                BrindeDAO.add_stock(brinde["id"], qtd, valor)
                MovimentacaoDAO.create_entrada(brinde["id"], qtd, valor, auth_manager.current_user["id"], just)
                
                event_manager.emit(EVENTS['STOCK_CHANGED'])
                
                dialog.safe_destroy()
                show_info("Sucesso", f"Entrada de {qtd} unidades registrada!")
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        dialog.add_buttons(save)
    
    def remove_stock(self, brinde):
        """Remove estoque"""
        dialog = FormDialog(self, f"Saída: {brinde['descricao']}", width=500, height=350)
        
        info_label = ctk.CTkLabel(dialog.content_frame, 
                                  text=f"Estoque atual: {brinde['quantidade']} {brinde['unidade']}",
                                  font=("Segoe UI", 12, "bold"))
        info_label.pack(pady=10)
        
        qtd_entry = dialog.add_field("Quantidade *")
        just_text = dialog.add_field("Justificativa *", "textbox")
        
        def save():
            try:
                qtd = int(qtd_entry.get())
                just = just_text.get("1.0", "end-1c")
                
                if not just:
                    show_error("Erro", "Justificativa é obrigatória!")
                    return
                
                if qtd > brinde["quantidade"]:
                    show_error("Erro", "Quantidade maior que estoque disponível!")
                    return
                
                BrindeDAO.remove_stock(brinde["id"], qtd)
                MovimentacaoDAO.create_saida(brinde["id"], qtd, auth_manager.current_user["id"], just)
                
                event_manager.emit(EVENTS['STOCK_CHANGED'])
                
                dialog.safe_destroy()
                show_info("Sucesso", f"Saída de {qtd} unidades registrada!")
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        dialog.add_buttons(save)
    
    def delete_brinde(self, brinde):
        """Exclui brinde com auditoria"""
        from ui.components.form_dialog import FormDialog
        
        # Dialog para motivo da exclusão
        dialog = FormDialog(self, f"Excluir: {brinde['descricao']}", width=500, height=300)
        
        # Campo para motivo
        motivo_text = dialog.add_field("Motivo da Exclusão *", "textbox")
        motivo_text.insert("1.0", "")
        
        # Label de aviso
        import customtkinter as ctk
        warning_label = ctk.CTkLabel(
            dialog.content_frame,
            text="⚠️ Esta ação irá excluir permanentemente o brinde.\nO registro ficará disponível no relatório de auditoria.",
            font=("Segoe UI", 11),
            text_color="#ff6b35",
            justify="center"
        )
        warning_label.pack(pady=10)
        
        def confirm_delete():
            motivo = motivo_text.get("1.0", "end-1c").strip()
            
            if not motivo:
                show_error("Erro", "Motivo da exclusão é obrigatório!")
                return
            
            try:
                # Usar os dados que já temos do brinde (que vem da view completa)
                brinde_completo = brinde
                
                # Registrar na auditoria ANTES de excluir
                
                usuario = auth_manager.current_user
                BrindeExcluidoDAO.create_from_brinde(
                    brinde_completo, 
                    usuario["id"], 
                    usuario["name"], 
                    motivo
                )
                
                # Agora excluir o brinde (vai excluir movimentações em cascata se configurado)
                BrindeDAO.delete(brinde["id"])
                
                # Emitir eventos
                event_manager.emit(EVENTS['BRINDE_DELETED'])
                event_manager.emit(EVENTS['STOCK_CHANGED'])
                
                dialog.safe_destroy()
                show_info("Sucesso", f"Brinde excluído com sucesso!\nRegistro salvo na auditoria.")
                
            except Exception as e:
                error_msg = str(e)
                if "FOREIGN KEY constraint failed" in error_msg:
                    show_error(
                        "Erro", 
                        "Erro de integridade do banco de dados.\nVerifique se existem registros dependentes."
                    )
                else:
                    show_error("Erro", f"Erro ao excluir: {error_msg}")
        
        dialog.add_buttons(confirm_delete)
    
    def show_filters_dialog(self):
        """Mostra dialog de filtros"""
        dialog = FormDialog(self, "Filtros Avançados", width=700, height=650)
        
        # Buscar dados para os combos
        categorias = CategoriaDAO.get_all()
        filiais = FilialDAO.get_all()
        fornecedores = FornecedorDAO.get_all()
        
        # Categoria
        cat_values = ["Todas"] + [c["nome"] for c in categorias]
        cat_combo = dialog.add_field("Categoria", "combobox", values=cat_values)
        cat_combo.set(self.filters["categoria"] or "Todas")
        
        # Filial (apenas ADMIN vê todas)
        if auth_manager.current_user["profile"] == "ADMIN":
            fil_values = ["Todas"] + [f"{f['numero']} - {f['nome']}" for f in filiais]
            fil_combo = dialog.add_field("Filial", "combobox", values=fil_values)
            fil_combo.set(self.filters["filial"] or "Todas")
        else:
            fil_combo = None
        
        # Fornecedor
        forn_values = ["Todos"] + [f["nome"] for f in fornecedores]
        forn_combo = dialog.add_field("Fornecedor", "combobox", values=forn_values)
        forn_combo.set(self.filters["fornecedor"] or "Todos")
        
        # Separador
        sep1 = ctk.CTkLabel(dialog.content_frame, text="Faixa de Valor", 
                           font=("Segoe UI", 12, "bold"))
        sep1.pack(pady=(10, 5))
        
        # Valor mínimo e máximo
        valor_frame = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        valor_frame.pack(fill="x", padx=20, pady=5)
        
        valor_min_label = ctk.CTkLabel(valor_frame, text="Mínimo:", font=("Segoe UI", 11))
        valor_min_label.pack(side="left", padx=5)
        valor_min_entry = ctk.CTkEntry(valor_frame, width=150, placeholder_text="R$ 0,00")
        if self.filters["valor_min"]:
            valor_min_entry.insert(0, str(self.filters["valor_min"]))
        valor_min_entry.pack(side="left", padx=5)
        
        valor_max_label = ctk.CTkLabel(valor_frame, text="Máximo:", font=("Segoe UI", 11))
        valor_max_label.pack(side="left", padx=(20, 5))
        valor_max_entry = ctk.CTkEntry(valor_frame, width=150, placeholder_text="R$ 999,99")
        if self.filters["valor_max"]:
            valor_max_entry.insert(0, str(self.filters["valor_max"]))
        valor_max_entry.pack(side="left", padx=5)
        
        # Separador
        sep2 = ctk.CTkLabel(dialog.content_frame, text="Faixa de Quantidade", 
                           font=("Segoe UI", 12, "bold"))
        sep2.pack(pady=(10, 5))
        
        # Quantidade mínima e máxima
        qtd_frame = ctk.CTkFrame(dialog.content_frame, fg_color="transparent")
        qtd_frame.pack(fill="x", padx=20, pady=5)
        
        qtd_min_label = ctk.CTkLabel(qtd_frame, text="Mínimo:", font=("Segoe UI", 11))
        qtd_min_label.pack(side="left", padx=5)
        qtd_min_entry = ctk.CTkEntry(qtd_frame, width=150, placeholder_text="0")
        if self.filters["qtd_min"] is not None:
            qtd_min_entry.insert(0, str(self.filters["qtd_min"]))
        qtd_min_entry.pack(side="left", padx=5)
        
        qtd_max_label = ctk.CTkLabel(qtd_frame, text="Máximo:", font=("Segoe UI", 11))
        qtd_max_label.pack(side="left", padx=(20, 5))
        qtd_max_entry = ctk.CTkEntry(qtd_frame, width=150, placeholder_text="9999")
        if self.filters["qtd_max"] is not None:
            qtd_max_entry.insert(0, str(self.filters["qtd_max"]))
        qtd_max_entry.pack(side="left", padx=5)
        
        def apply_filters():
            try:
                # Categoria
                cat_sel = cat_combo.get()
                self.filters["categoria"] = None if cat_sel == "Todas" else cat_sel
                
                # Filial
                if fil_combo:
                    fil_sel = fil_combo.get()
                    self.filters["filial"] = None if fil_sel == "Todas" else fil_sel
                
                # Fornecedor
                forn_sel = forn_combo.get()
                self.filters["fornecedor"] = None if forn_sel == "Todos" else forn_sel
                
                # Valor
                val_min = valor_min_entry.get().strip()
                self.filters["valor_min"] = float(val_min) if val_min else None
                
                val_max = valor_max_entry.get().strip()
                self.filters["valor_max"] = float(val_max) if val_max else None
                
                # Quantidade
                qtd_min = qtd_min_entry.get().strip()
                self.filters["qtd_min"] = int(qtd_min) if qtd_min else None
                
                qtd_max = qtd_max_entry.get().strip()
                self.filters["qtd_max"] = int(qtd_max) if qtd_max else None
                
                # Atualizar label de filtros ativos
                self._update_filters_label()
                
                # Recarregar lista
                self._safe_reload()
                
                dialog.safe_destroy()
                
            except ValueError:
                show_error("Erro", "Valores inválidos nos filtros!")
        
        dialog.add_buttons(apply_filters)
    
    def clear_filters(self):
        """Limpa todos os filtros"""
        self.filters = {
            "categoria": None,
            "filial": None,
            "fornecedor": None,
            "valor_min": None,
            "valor_max": None,
            "qtd_min": None,
            "qtd_max": None,
            "data_inicio": None,
            "data_fim": None
        }
        self._update_filters_label()
        self._safe_reload()
    
    def _update_filters_label(self):
        """Atualiza label de filtros ativos"""
        active = []
        if self.filters["categoria"]:
            active.append(f"Cat: {self.filters['categoria']}")
        if self.filters["filial"]:
            active.append(f"Fil: {self.filters['filial']}")
        if self.filters["fornecedor"]:
            active.append(f"Forn: {self.filters['fornecedor']}")
        if self.filters["valor_min"] or self.filters["valor_max"]:
            val_text = "Valor: "
            if self.filters["valor_min"]:
                val_text += f"R$ {self.filters['valor_min']:.2f}"
            val_text += " - "
            if self.filters["valor_max"]:
                val_text += f"R$ {self.filters['valor_max']:.2f}"
            active.append(val_text)
        if self.filters["qtd_min"] is not None or self.filters["qtd_max"] is not None:
            qtd_text = "Qtd: "
            if self.filters["qtd_min"] is not None:
                qtd_text += str(self.filters["qtd_min"])
            qtd_text += " - "
            if self.filters["qtd_max"] is not None:
                qtd_text += str(self.filters["qtd_max"])
            active.append(qtd_text)
        
        if active:
            self.active_filters_label.configure(text=f"Filtros: {' | '.join(active)}")
        else:
            self.active_filters_label.configure(text="")
