# -*- coding: utf-8 -*-
"""
Configuração de Fornecedores
"""
import customtkinter as ctk
from config.settings import COLORS
from database.dao import FornecedorDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from utils.event_manager import event_manager, EVENTS


class FornecedoresConfig(ctk.CTkFrame):
    """Configuração de Fornecedores"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        self._create_widgets()
        self.load_data()
        
        event_manager.subscribe(EVENTS['FORNECEDOR_CHANGED'], lambda d: self._safe_reload())
    
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
            text="➕ Novo Fornecedor",
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
        """Carrega fornecedores"""
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
        
        fornecedores = FornecedorDAO.get_all(ativo_apenas=False)
        
        for forn in fornecedores:
            self._create_row(forn)
    
    def _create_row(self, forn):
        """Cria linha de fornecedor"""
        row = ctk.CTkFrame(self.list_frame, fg_color="#f8f9fa", corner_radius=5)
        row.pack(fill="x", padx=10, pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(info_frame, text=forn["nome"], 
                                  font=("Segoe UI", 14, "bold"))
        name_label.pack(anchor="w")
        
        details = f"CNPJ: {forn['cnpj'] or 'N/A'} | Contato: {forn['contato'] or 'N/A'} | Tel: {forn['telefone'] or 'N/A'}"
        details_label = ctk.CTkLabel(info_frame, text=details, 
                                     font=("Segoe UI", 10), text_color="#666")
        details_label.pack(anchor="w")
        
        # Botões
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Editar", width=90,
                                 command=lambda: self.edit(forn))
        edit_btn.pack(side="left", padx=3)
        
        if forn["ativo"]:
            status_btn = ctk.CTkButton(btn_frame, text="🚫 Desativar", width=90,
                                       fg_color=COLORS["warning"],
                                       command=lambda: self.toggle_status(forn, False))
        else:
            status_btn = ctk.CTkButton(btn_frame, text="✅ Ativar", width=90,
                                       fg_color=COLORS["success"],
                                       command=lambda: self.toggle_status(forn, True))
        status_btn.pack(side="left", padx=3)
        
        # Botão excluir permanente
        delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Excluir", width=90,
                                    fg_color=COLORS["danger"],
                                    hover_color="#a71d2a",
                                    command=lambda: self.delete_permanent(forn))
        delete_btn.pack(side="left", padx=3)
    
    def show_new_form(self):
        """Formulário novo fornecedor"""
        dialog = FormDialog(self, "Novo Fornecedor", width=600, height=700)
        
        nome_entry = dialog.add_field("Nome *")
        cnpj_entry = dialog.add_field("CNPJ")
        contato_entry = dialog.add_field("Contato")
        telefone_entry = dialog.add_field("Telefone")
        email_entry = dialog.add_field("E-mail")
        endereco_entry = dialog.add_field("Endereço")
        cidade_entry = dialog.add_field("Cidade")
        estado_entry = dialog.add_field("Estado (UF)")
        cep_entry = dialog.add_field("CEP")
        obs_text = dialog.add_field("Observações", "textbox")
        
        def save():
            if not nome_entry.get():
                show_error("Erro", "Nome é obrigatório!")
                return
            
            try:
                data = {
                    "nome": nome_entry.get(),
                    "cnpj": cnpj_entry.get() or None,
                    "contato": contato_entry.get() or None,
                    "telefone": telefone_entry.get() or None,
                    "email": email_entry.get() or None,
                    "endereco": endereco_entry.get() or None,
                    "cidade": cidade_entry.get() or None,
                    "estado": estado_entry.get() or None,
                    "cep": cep_entry.get() or None,
                    "observacoes": obs_text.get("1.0", "end-1c") or None
                }
                
                FornecedorDAO.create(data)
                event_manager.emit(EVENTS['FORNECEDOR_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Fornecedor cadastrado!")
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        dialog.add_buttons(save)
    
    def edit(self, forn):
        """Edita fornecedor"""
        dialog = FormDialog(self, f"Editar: {forn['nome']}", width=600, height=700)
        
        nome_entry = dialog.add_field("Nome *")
        nome_entry.insert(0, forn["nome"])
        
        cnpj_entry = dialog.add_field("CNPJ")
        if forn.get("cnpj"): cnpj_entry.insert(0, forn["cnpj"])
        
        contato_entry = dialog.add_field("Contato")
        if forn.get("contato"): contato_entry.insert(0, forn["contato"])
        
        telefone_entry = dialog.add_field("Telefone")
        if forn.get("telefone"): telefone_entry.insert(0, forn["telefone"])
        
        email_entry = dialog.add_field("E-mail")
        if forn.get("email"): email_entry.insert(0, forn["email"])
        
        endereco_entry = dialog.add_field("Endereço")
        if forn.get("endereco"): endereco_entry.insert(0, forn["endereco"])
        
        cidade_entry = dialog.add_field("Cidade")
        if forn.get("cidade"): cidade_entry.insert(0, forn["cidade"])
        
        estado_entry = dialog.add_field("Estado (UF)")
        if forn.get("estado"): estado_entry.insert(0, forn["estado"])
        
        cep_entry = dialog.add_field("CEP")
        if forn.get("cep"): cep_entry.insert(0, forn["cep"])
        
        obs_text = dialog.add_field("Observações", "textbox")
        if forn.get("observacoes"): obs_text.insert("1.0", forn["observacoes"])
        
        def save():
            try:
                data = {
                    "nome": nome_entry.get(),
                    "cnpj": cnpj_entry.get() or None,
                    "contato": contato_entry.get() or None,
                    "telefone": telefone_entry.get() or None,
                    "email": email_entry.get() or None,
                    "endereco": endereco_entry.get() or None,
                    "cidade": cidade_entry.get() or None,
                    "estado": estado_entry.get() or None,
                    "cep": cep_entry.get() or None,
                    "observacoes": obs_text.get("1.0", "end-1c") or None
                }
                
                FornecedorDAO.update(forn["id"], data)
                event_manager.emit(EVENTS['FORNECEDOR_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Fornecedor atualizado!")
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        dialog.add_buttons(save)
    
    def toggle_status(self, forn, ativar):
        """Ativa/Desativa fornecedor"""
        def confirm():
            try:
                if ativar:
                    FornecedorDAO.activate(forn["id"])
                    msg = "Fornecedor ativado!"
                else:
                    FornecedorDAO.delete(forn["id"])
                    msg = "Fornecedor desativado!"
                
                event_manager.emit(EVENTS['FORNECEDOR_CHANGED'])
                show_info("Sucesso", msg)
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        ConfirmDialog(
            self,
            "Confirmar",
            f"Deseja {'ativar' if ativar else 'desativar'} o fornecedor '{forn['nome']}'?",
            confirm
        )
    
    def delete_permanent(self, forn):
        """Exclui fornecedor permanentemente"""
        def confirm():
            try:
                from database.connection import db
                
                # Verificar se há brindes usando este fornecedor
                check_query = "SELECT COUNT(*) as count FROM brindes WHERE fornecedor_id = ?"
                result = db.execute_query(check_query, (forn["id"],))
                
                if result[0]['count'] > 0:
                    # Remover a referência do fornecedor nos brindes primeiro
                    update_query = "UPDATE brindes SET fornecedor_id = NULL WHERE fornecedor_id = ?"
                    db.execute_update(update_query, (forn["id"],))
                    
                    show_warning(
                        "Aviso",
                        f"Existem {result[0]['count']} brindes associados a este fornecedor.\n" +
                        "A referência ao fornecedor foi removida dos brindes."
                    )
                
                # Excluir permanentemente
                delete_query = "DELETE FROM fornecedores WHERE id = ?"
                db.execute_update(delete_query, (forn["id"],))
                
                event_manager.emit(EVENTS['FORNECEDOR_CHANGED'])
                show_info("Sucesso", "Fornecedor excluído permanentemente!")
                
            except Exception as e:
                error_msg = str(e)
                if "FOREIGN KEY constraint failed" in error_msg:
                    show_error("Erro", "Não é possível excluir este fornecedor.\nExistem registros dependentes.")
                else:
                    show_error("Erro", f"Erro ao excluir: {error_msg}")
        
        ConfirmDialog(
            self,
            "⚠️ ATENÇÃO - Exclusão Permanente",
            f"Deseja EXCLUIR PERMANENTEMENTE o fornecedor '{forn['nome']}'?\n\n" +
            "Esta ação NÃO PODE SER DESFEITA!\n\n" +
            "Recomendamos usar 'Desativar' ao invés de excluir.",
            confirm
        )
