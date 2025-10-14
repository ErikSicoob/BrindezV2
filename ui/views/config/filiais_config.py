# -*- coding: utf-8 -*-
"""
Configuração de Filiais
"""
import customtkinter as ctk
from config.settings import COLORS
from database.dao import FilialDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from utils.event_manager import event_manager, EVENTS
from utils.auth import auth_manager


class FiliaisConfig(ctk.CTkFrame):
    """Configuração de Filiais"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        
        # Verificar permissão
        if not auth_manager.has_permission("admin"):
            self._show_no_permission()
            return
        
        self._create_widgets()
        self.load_data()
        
        event_manager.subscribe(EVENTS['FILIAL_CHANGED'], lambda d: self._safe_reload())
    
    def _safe_reload(self):
        """Recarrega a lista de forma segura, verificando se a view ainda existe"""
        try:
            if hasattr(self, 'winfo_exists') and self.winfo_exists():
                self.load_data()
        except Exception as e:
            from utils.logger import logger
            logger.debug(f"View não existe mais durante _safe_reload: {e}")
    
    def _show_no_permission(self):
        """Mostra mensagem de sem permissão"""
        label = ctk.CTkLabel(
            self,
            text="⛔ Você não tem permissão para acessar esta área.\nApenas Administradores podem gerenciar filiais.",
            font=("Segoe UI", 14),
            text_color=COLORS["danger"]
        )
        label.pack(expand=True)
    
    def _create_widgets(self):
        """Cria widgets"""
        # Botão novo
        new_btn = ctk.CTkButton(
            self,
            text="➕ Nova Filial",
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
        """Carrega filiais"""
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
        
        filiais = FilialDAO.get_all(ativo_apenas=False)
        
        if not filiais:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma filial cadastrada",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data.pack(pady=50)
        else:
            for fil in filiais:
                self._create_row(fil)
    
    def _create_row(self, fil):
        """Cria linha de filial"""
        row = ctk.CTkFrame(self.list_frame, fg_color="#f8f9fa", corner_radius=5)
        row.pack(fill="x", padx=10, pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=f"{fil['numero']} - {fil['nome']}", 
            font=("Segoe UI", 14, "bold")
        )
        name_label.pack(anchor="w")
        
        details = f"📍 {fil['cidade']}"
        if fil.get("estado"):
            details += f"/{fil['estado']}"
        if fil.get("responsavel"):
            details += f" | 👤 {fil['responsavel']}"
        if fil.get("telefone"):
            details += f" | 📞 {fil['telefone']}"
        
        details_label = ctk.CTkLabel(info_frame, text=details, 
                                     font=("Segoe UI", 10), text_color="#666")
        details_label.pack(anchor="w")
        
        # Status
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {'✅ Ativo' if fil['ativo'] else '🚫 Inativo'}",
            font=("Segoe UI", 9),
            text_color=COLORS["success"] if fil['ativo'] else COLORS["danger"]
        )
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Botões
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Editar", width=90,
                                 command=lambda: self.edit(fil))
        edit_btn.pack(side="left", padx=3)
        
        if fil["ativo"]:
            status_btn = ctk.CTkButton(btn_frame, text="🚫 Desativar", width=90,
                                       fg_color=COLORS["warning"],
                                       command=lambda: self.toggle_status(fil, False))
        else:
            status_btn = ctk.CTkButton(btn_frame, text="✅ Ativar", width=90,
                                       fg_color=COLORS["success"],
                                       command=lambda: self.toggle_status(fil, True))
        status_btn.pack(side="left", padx=3)
        
        # Botão excluir permanente
        delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Excluir", width=90,
                                    fg_color=COLORS["danger"],
                                    hover_color="#a71d2a",
                                    command=lambda: self.delete_permanent(fil))
        delete_btn.pack(side="left", padx=3)
    
    def show_new_form(self):
        """Formulário nova filial"""
        dialog = FormDialog(self, "Nova Filial", width=600, height=650)
        
        numero_entry = dialog.add_field("Número *")
        nome_entry = dialog.add_field("Nome *")
        cidade_entry = dialog.add_field("Cidade *")
        estado_entry = dialog.add_field("Estado (UF)")
        endereco_entry = dialog.add_field("Endereço")
        telefone_entry = dialog.add_field("Telefone")
        email_entry = dialog.add_field("E-mail")
        responsavel_entry = dialog.add_field("Responsável")
        
        def save():
            numero = numero_entry.get().strip()
            nome = nome_entry.get().strip()
            cidade = cidade_entry.get().strip()
            
            if not numero or not nome or not cidade:
                show_error("Erro", "Número, Nome e Cidade são obrigatórios!")
                return
            
            # Verificar se já existe filial com este número
            filiais_existentes = FilialDAO.get_all(ativo_apenas=False)
            if any(f["numero"] == numero for f in filiais_existentes):
                show_error("Erro", f"Já existe uma filial com o número '{numero}'!")
                return
            
            try:
                data = {
                    "numero": numero,
                    "nome": nome,
                    "cidade": cidade,
                    "estado": estado_entry.get().strip() or None,
                    "endereco": endereco_entry.get().strip() or None,
                    "telefone": telefone_entry.get().strip() or None,
                    "email": email_entry.get().strip() or None,
                    "responsavel": responsavel_entry.get().strip() or None
                }
                
                FilialDAO.create(data)
                event_manager.emit(EVENTS['FILIAL_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Filial cadastrada!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe uma filial com este número!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def edit(self, fil):
        """Edita filial"""
        dialog = FormDialog(self, f"Editar: {fil['nome']}", width=600, height=650)
        
        numero_entry = dialog.add_field("Número *")
        numero_entry.insert(0, fil["numero"])
        
        nome_entry = dialog.add_field("Nome *")
        nome_entry.insert(0, fil["nome"])
        
        cidade_entry = dialog.add_field("Cidade *")
        cidade_entry.insert(0, fil["cidade"])
        
        estado_entry = dialog.add_field("Estado (UF)")
        if fil.get("estado"):
            estado_entry.insert(0, fil["estado"])
        
        endereco_entry = dialog.add_field("Endereço")
        if fil.get("endereco"):
            endereco_entry.insert(0, fil["endereco"])
        
        telefone_entry = dialog.add_field("Telefone")
        if fil.get("telefone"):
            telefone_entry.insert(0, fil["telefone"])
        
        email_entry = dialog.add_field("E-mail")
        if fil.get("email"):
            email_entry.insert(0, fil["email"])
        
        responsavel_entry = dialog.add_field("Responsável")
        if fil.get("responsavel"):
            responsavel_entry.insert(0, fil["responsavel"])
        
        def save():
            numero = numero_entry.get().strip()
            nome = nome_entry.get().strip()
            cidade = cidade_entry.get().strip()
            
            if not numero or not nome or not cidade:
                show_error("Erro", "Número, Nome e Cidade são obrigatórios!")
                return
            
            # Verificar se já existe outra filial com este número
            filiais_existentes = FilialDAO.get_all(ativo_apenas=False)
            if any(f["numero"] == numero and f["id"] != fil["id"] for f in filiais_existentes):
                show_error("Erro", f"Já existe outra filial com o número '{numero}'!")
                return
            
            try:
                data = {
                    "numero": numero,
                    "nome": nome,
                    "cidade": cidade,
                    "estado": estado_entry.get().strip() or None,
                    "endereco": endereco_entry.get().strip() or None,
                    "telefone": telefone_entry.get().strip() or None,
                    "email": email_entry.get().strip() or None,
                    "responsavel": responsavel_entry.get().strip() or None
                }
                
                FilialDAO.update(fil["id"], data)
                event_manager.emit(EVENTS['FILIAL_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Filial atualizada!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe uma filial com este número!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def toggle_status(self, fil, ativar):
        """Ativa/Desativa filial"""
        def confirm():
            try:
                if not ativar:
                    # Verificar se há usuários ou brindes nesta filial
                    from database.connection import db
                    
                    check_users = "SELECT COUNT(*) as count FROM usuarios WHERE filial_id = ? AND ativo = 1"
                    result_users = db.execute_query(check_users, (fil["id"],))
                    
                    check_brindes = "SELECT COUNT(*) as count FROM brindes WHERE filial_id = ?"
                    result_brindes = db.execute_query(check_brindes, (fil["id"],))
                    
                    if result_users[0]['count'] > 0:
                        show_error(
                            "Erro",
                            f"Não é possível desativar!\nExistem {result_users[0]['count']} usuários ativos nesta filial."
                        )
                        return
                    
                    if result_brindes[0]['count'] > 0:
                        show_error(
                            "Erro",
                            f"Não é possível desativar!\nExistem {result_brindes[0]['count']} brindes nesta filial."
                        )
                        return
                
                if ativar:
                    FilialDAO.activate(fil["id"])
                    msg = "Filial ativada!"
                else:
                    FilialDAO.delete(fil["id"])
                    msg = "Filial desativada!"
                
                event_manager.emit(EVENTS['FILIAL_CHANGED'])
                show_info("Sucesso", msg)
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        ConfirmDialog(
            self,
            "Confirmar",
            f"Deseja {'ativar' if ativar else 'desativar'} a filial '{fil['nome']}'?",
            confirm
        )
    
    def delete_permanent(self, fil):
        """Exclui filial permanentemente"""
        def confirm():
            try:
                # Verificar se há usuários ou brindes
                from database.connection import db
                
                check_users = "SELECT COUNT(*) as count FROM usuarios WHERE filial_id = ?"
                result_users = db.execute_query(check_users, (fil["id"],))
                
                check_brindes = "SELECT COUNT(*) as count FROM brindes WHERE filial_id = ?"
                result_brindes = db.execute_query(check_brindes, (fil["id"],))
                
                if result_users[0]['count'] > 0 or result_brindes[0]['count'] > 0:
                    show_error(
                        "Erro",
                        f"Não é possível excluir!\n\n" +
                        f"Usuários: {result_users[0]['count']}\n" +
                        f"Brindes: {result_brindes[0]['count']}\n\n" +
                        "Desative a filial ao invés de excluir."
                    )
                    return
                
                # Excluir permanentemente
                delete_query = "DELETE FROM filiais WHERE id = ?"
                db.execute_update(delete_query, (fil["id"],))
                
                event_manager.emit(EVENTS['FILIAL_CHANGED'])
                show_info("Sucesso", "Filial excluída permanentemente!")
                
            except Exception as e:
                show_error("Erro", f"Erro ao excluir: {str(e)}")
        
        # Confirmação única
        ConfirmDialog(
            self,
            "⚠️ ATENÇÃO - Exclusão Permanente",
            f"Deseja EXCLUIR PERMANENTEMENTE a filial '{fil['nome']}'?\n\n" +
            "Esta ação NÃO PODE SER DESFEITA!\n\n" +
            "Recomendamos usar 'Desativar' ao invés de excluir.",
            confirm
        )
