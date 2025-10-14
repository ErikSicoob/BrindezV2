# -*- coding: utf-8 -*-
"""
Configuração de Unidades de Medida
"""
import customtkinter as ctk
from config.settings import COLORS
from database.dao import UnidadeDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from utils.event_manager import event_manager, EVENTS
from utils.auth import auth_manager

class UnidadesConfig(ctk.CTkFrame):
    """Configuração de Unidades de Medida"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self._create_widgets()
        self.load_data()
        
        event_manager.subscribe(EVENTS['UNIDADE_CHANGED'], lambda d: self._safe_reload())
    
    def _safe_reload(self):
        """Recarrega a lista de forma segura, verificando se a view ainda existe"""
        try:
            if hasattr(self, 'winfo_exists') and self.winfo_exists():
                self.load_data()
        except Exception as e:
            from utils.logger import logger
            logger.debug(f"View não existe mais durante _safe_reload: {e}")
    
    def _create_widgets(self):
        """Cria widgets"""
        # Botão novo
        new_btn = ctk.CTkButton(
            self,
            text="➕ Nova Unidade",
            font=("Segoe UI", 14, "bold"),
            height=40,
            fg_color=COLORS["primary"],
            command=self.show_new_form
        )
        new_btn.pack(pady=(0, 20))
        
        # Lista
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=10)
        self.list_frame.pack(fill="both", expand=True)
    
    def load_data(self):
        """Carrega unidades"""
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
            from utils.logger import logger
            logger.debug(f"View destruída durante load_data: {e}")
            return
        
        unidades = UnidadeDAO.get_all(ativo_apenas=False)
        
        if not unidades:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma unidade cadastrada",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data.pack(pady=50)
        else:
            for un in unidades:
                self._create_row(un)
    
    def _create_row(self, un):
        """Cria linha de unidade"""
        row = ctk.CTkFrame(self.list_frame, fg_color="#f8f9fa", corner_radius=5)
        row.pack(fill="x", padx=10, pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"{un['codigo']} - {un['nome']}", 
            font=("Segoe UI", 14, "bold")
        )
        name_label.pack(anchor="w")
        
        if un.get("descricao"):
            desc_label = ctk.CTkLabel(info_frame, text=un["descricao"], 
                                     font=("Segoe UI", 10), text_color="#666")
            desc_label.pack(anchor="w")
        
        # Status
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {'✅ Ativo' if un['ativo'] else '🚫 Inativo'}",
            font=("Segoe UI", 9),
            text_color=COLORS["success"] if un['ativo'] else COLORS["danger"]
        )
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Botões
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Editar", width=90,
                                 command=lambda: self.edit_unidade(un))
        edit_btn.pack(side="left", padx=3)
        
        # Apenas ADMIN pode desativar/excluir
        from utils.auth import auth_manager
        if auth_manager.has_permission("admin"):
            if un["ativo"]:
                status_btn = ctk.CTkButton(btn_frame, text="🚫 Desativar", width=90,
                                           fg_color=COLORS["warning"],
                                           command=lambda: self.toggle_status(un, False))
            else:
                status_btn = ctk.CTkButton(btn_frame, text="✅ Ativar", width=90,
                                           fg_color=COLORS["success"],
                                           command=lambda: self.toggle_status(un, True))
            status_btn.pack(side="left", padx=3)
            
            # Botão excluir permanente
            delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Excluir", width=90,
                                        fg_color=COLORS["danger"],
                                        hover_color="#a71d2a",
                                        command=lambda: self.delete_permanent(un))
            delete_btn.pack(side="left", padx=3)
    
    def show_new_form(self):
        """Formulário nova unidade"""
        dialog = FormDialog(self, "Nova Unidade de Medida", width=500, height=400)
        
        codigo_entry = dialog.add_field("Código *")
        nome_entry = dialog.add_field("Nome *")
        desc_text = dialog.add_field("Descrição", "textbox")
        
        def save():
            codigo = codigo_entry.get().strip().upper()
            nome = nome_entry.get().strip()
            
            if not codigo or not nome:
                show_error("Erro", "Código e Nome são obrigatórios!")
                return
            
            # Verificar se já existe
            unidades_existentes = UnidadeDAO.get_all(ativo_apenas=False)
            if any(u["codigo"] == codigo for u in unidades_existentes):
                show_error("Erro", f"Já existe uma unidade com o código '{codigo}'!")
                return
            
            try:
                data = {
                    "codigo": codigo,
                    "nome": nome,
                    "descricao": desc_text.get("1.0", "end-1c").strip() or None
                }
                
                UnidadeDAO.create(data)
                event_manager.emit(EVENTS['UNIDADE_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Unidade cadastrada!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe uma unidade com este código!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def edit_unidade(self, un):
        """Edita unidade"""
        dialog = FormDialog(self, f"Editar: {un['codigo']}", width=500, height=400)
        
        codigo_entry = dialog.add_field("Código *")
        codigo_entry.insert(0, un["codigo"])
        
        nome_entry = dialog.add_field("Nome *")
        nome_entry.insert(0, un["nome"])
        
        desc_text = dialog.add_field("Descrição", "textbox")
        if un.get("descricao"):
            desc_text.insert("1.0", un["descricao"])
        
        def save():
            codigo = codigo_entry.get().strip().upper()
            nome = nome_entry.get().strip()
            
            if not codigo or not nome:
                show_error("Erro", "Código e Nome são obrigatórios!")
                return
            
            # Verificar se já existe (exceto a própria unidade)
            unidades_existentes = UnidadeDAO.get_all(ativo_apenas=False)
            if any(u["codigo"] == codigo and u["id"] != un["id"] for u in unidades_existentes):
                show_error("Erro", f"Já existe outra unidade com o código '{codigo}'!")
                return
            
            try:
                data = {
                    "codigo": codigo,
                    "nome": nome,
                    "descricao": desc_text.get("1.0", "end-1c").strip() or None
                }
                
                UnidadeDAO.update(un["id"], data)
                event_manager.emit(EVENTS['UNIDADE_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Unidade atualizada!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe uma unidade com este código!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def toggle_status(self, un, ativar):
        """Ativa/Desativa unidade"""
        def confirm():
            try:
                if not ativar:
                    # Verificar se há brindes usando esta unidade
                    from database.connection import db
                    check_query = "SELECT COUNT(*) as count FROM brindes WHERE unidade_id = ?"
                    result = db.execute_query(check_query, (un["id"],))
                    if result[0]['count'] > 0:
                        show_error(
                            "Erro",
                            f"Não é possível desativar!\nExistem {result[0]['count']} brindes usando esta unidade."
                        )
                        return
                
                if ativar:
                    UnidadeDAO.activate(un["id"])
                    msg = "Unidade ativada!"
                else:
                    UnidadeDAO.delete(un["id"])
                    msg = "Unidade desativada!"
                
                event_manager.emit(EVENTS['UNIDADE_CHANGED'])
                show_info("Sucesso", msg)
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        ConfirmDialog(
            self,
            "Confirmar",
            f"Deseja {'ativar' if ativar else 'desativar'} a unidade '{un['codigo']}'?",
            confirm
        )
    
    def delete_permanent(self, un):
        """Exclui unidade permanentemente"""
        def confirm():
            try:
                # Verificar se há brindes usando esta unidade
                from database.connection import db
                check_query = "SELECT COUNT(*) as count FROM brindes WHERE unidade_id = ?"
                result = db.execute_query(check_query, (un["id"],))
                if result[0]['count'] > 0:
                    show_error(
                        "Erro",
                        f"Não é possível excluir!\nExistem {result[0]['count']} brindes usando esta unidade.\n\nDesative a unidade ao invés de excluir."
                    )
                    return
                
                # Excluir permanentemente
                delete_query = "DELETE FROM unidades_medida WHERE id = ?"
                db.execute_update(delete_query, (un["id"],))
                
                event_manager.emit(EVENTS['UNIDADE_CHANGED'])
                show_info("Sucesso", "Unidade excluída permanentemente!")
                
            except Exception as e:
                show_error("Erro", f"Erro ao excluir: {str(e)}")
        
        # Confirmação única
        ConfirmDialog(
            self,
            "⚠️ ATENÇÃO - Exclusão Permanente",
            f"Deseja EXCLUIR PERMANENTEMENTE a unidade '{un['codigo']}'?\n\n" +
            "Esta ação NÃO PODE SER DESFEITA!\n\n" +
            "Recomendamos usar 'Desativar' ao invés de excluir.",
            confirm
        )
