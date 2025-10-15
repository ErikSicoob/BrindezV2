# -*- coding: utf-8 -*-
"""
Tela de Gestão de Brindes - Versão Completa com BD
"""
import customtkinter as ctk
from config.settings import COLORS
from database.dao import BrindeDAO, CategoriaDAO, UnidadeDAO, FilialDAO, FornecedorDAO, MovimentacaoDAO, BrindeExcluidoDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from ui.components.multi_filial_selector import MultiFilialSelector
from ui.components.expandable_card import ExpandableCard
from utils.event_manager import event_manager, EVENTS
from utils.auth import auth_manager


class BrindesView(ctk.CTkFrame):
    """View de gestão de brindes"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLORS["content_bg"])
        self.selected_brinde = None
        
        # Filtros
        self.filters = {
            "categoria": None,
            "filial": None,
            "fornecedor": None,
            "ordem_valor": None,  # "asc" ou "desc"
            "ordem_qtd": None,    # "asc" ou "desc"
            "data_inicio": None,
            "data_fim": None
        }
        
        self._create_widgets()
        self.load_brindes_grouped()
        
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
                self.load_brindes_grouped()
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
        
        # Container de lista
        list_container = ctk.CTkFrame(main_container, fg_color="white", corner_radius=10)
        list_container.pack(fill="both", expand=True)
        
        # Cabeçalho removido - visualização agrupada não precisa
        
        # Lista
        self.list_frame = ctk.CTkScrollableFrame(list_container, fg_color="transparent", corner_radius=0)
        self.list_frame.pack(fill="both", expand=True)
        
        # Paginação removida - visualização agrupada não usa paginação
    
    # Método _create_brinde_row removido - não usado mais na visualização agrupada
    
    # Método load_brindes removido - usando apenas load_brindes_grouped
    
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
        
        # Ordenar por valor
        if self.filters["ordem_valor"]:
            reverse = self.filters["ordem_valor"] == "desc"
            filtered = sorted(filtered, key=lambda x: x.get("valor_unitario", 0), reverse=reverse)
        
        # Ordenar por quantidade
        if self.filters["ordem_qtd"]:
            reverse = self.filters["ordem_qtd"] == "desc"
            filtered = sorted(filtered, key=lambda x: x.get("quantidade", 0), reverse=reverse)
        
        return filtered
    
    # Métodos de paginação e alternância de visualização removidos
    
    def load_brindes_grouped(self):
        """Carrega lista de brindes agrupados por descrição com filtros aplicados"""
        try:
            if not hasattr(self, 'list_frame') or not self.list_frame.winfo_exists():
                return
        except:
            return
        
        try:
            for widget in self.list_frame.winfo_children():
                widget.destroy()
        except Exception as e:
            from utils.logger import logger
            logger.debug(f"View destruída durante load_brindes_grouped: {e}")
            return
        
        # Buscar brindes agrupados
        brindes_grouped = BrindeDAO.get_grouped_by_description()
        
        # Aplicar filtros no agrupamento
        brindes_grouped = self._apply_filters_grouped(brindes_grouped)
        
        if not brindes_grouped:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Nenhum brinde encontrado",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data.pack(pady=50)
            return
        
        # Criar cards expandíveis
        for brinde_group in brindes_grouped:
            # Buscar detalhes por filial
            detalhes = BrindeDAO.get_by_description(brinde_group['descricao'])
            
            # Aplicar filtros nos detalhes
            detalhes = self._apply_filters(detalhes)
            
            # Se após filtrar não sobrar nenhum detalhe, pular este brinde
            if not detalhes:
                continue
            
            # Criar título do card
            title = f"{brinde_group['descricao']}"
            if brinde_group.get('codigo_interno'):
                title += f" ({brinde_group['codigo_interno']})"
            
            # Criar card
            card = ExpandableCard(
                self.list_frame,
                title=title,
                data=detalhes,
                on_edit=self.edit_brinde,
                on_add_stock=self.add_stock,
                on_remove_stock=self.remove_stock,
                on_transfer=self.transfer_brinde,
                on_delete=self.delete_brinde
            )
            card.pack(fill="x", padx=5, pady=5)
    
    def _apply_filters_grouped(self, brindes_grouped):
        """Aplica filtros aos brindes agrupados"""
        filtered = brindes_grouped
        
        # Filtro por categoria
        if self.filters["categoria"]:
            filtered = [b for b in filtered if b.get("categoria") == self.filters["categoria"]]
        
        # Filtro por fornecedor
        if self.filters["fornecedor"]:
            filtered = [b for b in filtered if b.get("fornecedor") == self.filters["fornecedor"]]
        
        # Ordenar por valor médio
        if self.filters["ordem_valor"]:
            reverse = self.filters["ordem_valor"] == "desc"
            filtered = sorted(filtered, key=lambda x: x.get("valor_medio", 0), reverse=reverse)
        
        # Ordenar por quantidade total
        if self.filters["ordem_qtd"]:
            reverse = self.filters["ordem_qtd"] == "desc"
            filtered = sorted(filtered, key=lambda x: x.get("quantidade_total", 0), reverse=reverse)
        
        return filtered
    
    def show_new_brinde_form(self):
        """Mostra formulário de novo brinde com suporte a múltiplas filiais"""
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
        
        dialog = FormDialog(self, "Novo Brinde", width=750, height=700)
        
        # Campos
        desc_entry = dialog.add_field("Descrição *")
        qtd_entry = dialog.add_field("Quantidade Total *")
        qtd_entry.insert(0, "0")
        valor_entry = dialog.add_field("Valor Unitário *")
        
        cat_combo = dialog.add_field("Categoria *", "combobox", 
                                     values=[c["nome"] for c in categorias])
        cat_combo.set(categorias[0]["nome"])
        
        un_combo = dialog.add_field("Unidade de Medida *", "combobox",
                                    values=[f"{u['codigo']} - {u['nome']}" for u in unidades])
        un_combo.set(f"{unidades[0]['codigo']} - {unidades[0]['nome']}")
        
        forn_combo = dialog.add_field("Fornecedor", "combobox",
                                      values=["Nenhum"] + [f["nome"] for f in fornecedores])
        forn_combo.set("Nenhum")
        
        cod_entry = dialog.add_field("Código Interno")
        obs_text = dialog.add_field("Observações", "textbox")
        estoque_min_entry = dialog.add_field("Estoque Mínimo")
        estoque_min_entry.insert(0, "10")
        
        # Separador
        sep_label = ctk.CTkLabel(
            dialog.content_frame,
            text="═" * 60,
            font=("Segoe UI", 10),
            text_color="#cccccc"
        )
        sep_label.pack(pady=10)
        
        # Seletor de múltiplas filiais
        filial_label = ctk.CTkLabel(
            dialog.content_frame,
            text="Distribuição por Filiais",
            font=("Segoe UI", 12, "bold")
        )
        filial_label.pack(anchor="w", padx=20, pady=(5, 10))
        
        multi_filial_selector = MultiFilialSelector(
            dialog.content_frame,
            filiais=filiais,
            quantidade_total_callback=lambda: qtd_entry.get()
        )
        multi_filial_selector.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        
        def save():
            # Validar
            if not desc_entry.get() or not valor_entry.get():
                show_error("Erro", "Preencha todos os campos obrigatórios!")
                return
            
            try:
                quantidade_total = int(qtd_entry.get() or 0)
                
                if quantidade_total <= 0:
                    show_error("Erro", "Quantidade total deve ser maior que zero!")
                    return
                
                # Obter distribuição de filiais
                distribuicao = multi_filial_selector.get_distribuicao()
                
                # Validar distribuição
                valid, msg = multi_filial_selector.validate(quantidade_total)
                if not valid:
                    show_error("Erro", msg)
                    return
                
                # Obter IDs
                cat_nome = cat_combo.get()
                categoria = next((c for c in categorias if c["nome"] == cat_nome), None)
                
                un_codigo = un_combo.get().split(" - ")[0]
                unidade = next((u for u in unidades if u["codigo"] == un_codigo), None)
                
                forn_nome = forn_combo.get()
                fornecedor = next((f for f in fornecedores if f["nome"] == forn_nome), None) if forn_nome != "Nenhum" else None
                
                # Dados do brinde (sem filial_id e quantidade)
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
                
                # Se modo único, usar quantidade total
                if not multi_filial_selector.modo_multiplo.get():
                    filial_id = list(distribuicao.keys())[0]
                    distribuicao[filial_id] = quantidade_total
                
                # Criar brinde(s)
                BrindeDAO.create_multi_filial(data, distribuicao)
                
                event_manager.emit(EVENTS['BRINDE_CREATED'])
                event_manager.emit(EVENTS['STOCK_CHANGED'])
                
                dialog.safe_destroy()
                num_filiais = len(distribuicao)
                show_info("Sucesso", f"Brinde cadastrado com sucesso em {num_filiais} filiai{'s' if num_filiais > 1 else ''}!")
                
            except Exception as e:
                show_error("Erro", f"Erro ao cadastrar brinde: {str(e)}")
                import traceback
                traceback.print_exc()
        
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
    
    def transfer_brinde(self, brinde):
        """Transfere brinde para outra filial"""
        from database.dao import FilialDAO, TransferenciaDAO
        
        # Buscar filiais (exceto a atual)
        todas_filiais = FilialDAO.get_all()
        outras_filiais = [f for f in todas_filiais if f['id'] != brinde['filial_id']]
        
        if not outras_filiais:
            show_error("Erro", "Não há outras filiais disponíveis para transferência!")
            return
        
        dialog = FormDialog(self, f"Transferir: {brinde['descricao']}", width=500, height=400)
        
        # Informações do brinde
        info_frame = ctk.CTkFrame(dialog.content_frame, fg_color="#e3f2fd", corner_radius=5)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_label = ctk.CTkLabel(
            info_frame,
            text=f"📦 Filial Origem: {brinde['filial']}\n📊 Estoque Atual: {brinde['quantidade']} {brinde['unidade']}",
            font=("Segoe UI", 11),
            justify="left"
        )
        info_label.pack(pady=15, padx=10)
        
        # Filial destino
        filial_combo = dialog.add_field("Filial Destino *", "combobox",
                                        values=[f"{f['numero']} - {f['nome']}" for f in outras_filiais])
        filial_combo.set(f"{outras_filiais[0]['numero']} - {outras_filiais[0]['nome']}")
        
        # Quantidade
        qtd_entry = dialog.add_field("Quantidade a Transferir *")
        qtd_entry.insert(0, "0")
        
        # Observações
        obs_text = dialog.add_field("Observações", "textbox")
        
        def save():
            try:
                qtd = int(qtd_entry.get())
                obs = obs_text.get("1.0", "end-1c")
                
                if qtd <= 0:
                    show_error("Erro", "Quantidade deve ser maior que zero!")
                    return
                
                if qtd > brinde["quantidade"]:
                    show_error("Erro", f"Quantidade maior que estoque disponível ({brinde['quantidade']})!")
                    return
                
                # Obter filial destino
                fil_numero = filial_combo.get().split(" - ")[0]
                filial_destino = next((f for f in outras_filiais if f["numero"] == fil_numero), None)
                
                # Confirmar transferência
                def confirm_transfer():
                    # Realizar transferência
                    success = BrindeDAO.transfer(brinde["id"], filial_destino["id"], qtd)
                    
                    if success:
                        # Registrar na tabela de transferências
                        TransferenciaDAO.create(
                            brinde["id"],
                            brinde["filial_id"],
                            filial_destino["id"],
                            qtd,
                            auth_manager.current_user["id"],
                            obs
                        )
                        
                        event_manager.emit(EVENTS['STOCK_CHANGED'])
                        
                        dialog.safe_destroy()
                        show_info("Sucesso", f"Transferência de {qtd} unidades realizada com sucesso!")
                    else:
                        show_error("Erro", "Falha ao realizar transferência!")
                
                ConfirmDialog(
                    self,
                    "⚠️ Confirmar Transferência",
                    f"Transferir {qtd} {brinde['unidade']} de:\n"
                    f"  {brinde['filial']}\n"
                    f"Para:\n"
                    f"  {filial_destino['nome']}?",
                    confirm_transfer
                )
                
            except ValueError:
                show_error("Erro", "Quantidade inválida!")
            except Exception as e:
                show_error("Erro", f"Erro ao transferir: {str(e)}")
        
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
        sep1 = ctk.CTkLabel(dialog.content_frame, text="Ordenação", 
                           font=("Segoe UI", 12, "bold"))
        sep1.pack(pady=(10, 5))
        
        # Ordenação por valor
        ordem_valor_combo = dialog.add_field("Ordenar por Valor", "combobox",
                                             values=["Nenhuma", "Menor para Maior", "Maior para Menor"])
        if self.filters["ordem_valor"] == "asc":
            ordem_valor_combo.set("Menor para Maior")
        elif self.filters["ordem_valor"] == "desc":
            ordem_valor_combo.set("Maior para Menor")
        else:
            ordem_valor_combo.set("Nenhuma")
        
        # Ordenação por quantidade
        ordem_qtd_combo = dialog.add_field("Ordenar por Quantidade", "combobox",
                                           values=["Nenhuma", "Menor para Maior", "Maior para Menor"])
        if self.filters["ordem_qtd"] == "asc":
            ordem_qtd_combo.set("Menor para Maior")
        elif self.filters["ordem_qtd"] == "desc":
            ordem_qtd_combo.set("Maior para Menor")
        else:
            ordem_qtd_combo.set("Nenhuma")
        
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
                
                # Ordenação por valor
                ordem_valor_sel = ordem_valor_combo.get()
                if ordem_valor_sel == "Menor para Maior":
                    self.filters["ordem_valor"] = "asc"
                elif ordem_valor_sel == "Maior para Menor":
                    self.filters["ordem_valor"] = "desc"
                else:
                    self.filters["ordem_valor"] = None
                
                # Ordenação por quantidade
                ordem_qtd_sel = ordem_qtd_combo.get()
                if ordem_qtd_sel == "Menor para Maior":
                    self.filters["ordem_qtd"] = "asc"
                elif ordem_qtd_sel == "Maior para Menor":
                    self.filters["ordem_qtd"] = "desc"
                else:
                    self.filters["ordem_qtd"] = None
                
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
            "ordem_valor": None,
            "ordem_qtd": None,
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
        if self.filters["ordem_valor"]:
            ordem_text = "↑ Menor→Maior" if self.filters["ordem_valor"] == "asc" else "↓ Maior→Menor"
            active.append(f"Valor: {ordem_text}")
        if self.filters["ordem_qtd"]:
            ordem_text = "↑ Menor→Maior" if self.filters["ordem_qtd"] == "asc" else "↓ Maior→Menor"
            active.append(f"Qtd: {ordem_text}")
        
        if active:
            self.active_filters_label.configure(text=f"Filtros: {' | '.join(active)}")
        else:
            self.active_filters_label.configure(text="")

# Updated: 2025-10-15 14:17:00
