# -*- coding: utf-8 -*-
"""
Configuração de Usuários
"""
import customtkinter as ctk
from config.settings import COLORS, USER_PROFILES
from database.dao import UsuarioDAO, FilialDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from utils.event_manager import event_manager, EVENTS
from utils.auth import auth_manager


class UsuariosConfig(ctk.CTkFrame):
    """Configuração de Usuários"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        
        # Verificar permissão
        if not auth_manager.has_permission("admin"):
            self._show_no_permission()
            return
        
        self._create_widgets()
        self.load_data()
        
        event_manager.subscribe(EVENTS['USUARIO_CHANGED'], lambda d: self._safe_reload())
    
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
            text="⛔ Você não tem permissão para acessar esta área.\nApenas Administradores podem gerenciar usuários.",
            font=("Segoe UI", 14),
            text_color=COLORS["danger"]
        )
        label.pack(expand=True)
    
    def _create_widgets(self):
        """Cria widgets"""
        # Botão novo
        new_btn = ctk.CTkButton(
            self,
            text="➕ Novo Usuário",
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
        """Carrega usuários"""
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
        
        usuarios = UsuarioDAO.get_all(ativo_apenas=False)
        
        if not usuarios:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Nenhum usuário cadastrado",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data.pack(pady=50)
        else:
            for usr in usuarios:
                self._create_row(usr)
    
    def _create_row(self, usr):
        """Cria linha de usuário"""
        row = ctk.CTkFrame(self.list_frame, fg_color="#f8f9fa", corner_radius=5)
        row.pack(fill="x", padx=10, pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(info_frame, text=usr["nome"], 
                                  font=("Segoe UI", 14, "bold"))
        name_label.pack(anchor="w")
        
        details = f"👤 {usr['username']} | 🏢 {usr['filial_nome']} | 🔑 {usr['perfil']}"
        if usr.get("email"):
            details += f" | 📧 {usr['email']}"
        
        details_label = ctk.CTkLabel(info_frame, text=details, 
                                     font=("Segoe UI", 10), text_color="#666")
        details_label.pack(anchor="w")
        
        # Status
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {'✅ Ativo' if usr['ativo'] else '🚫 Inativo'}",
            font=("Segoe UI", 9),
            text_color=COLORS["success"] if usr['ativo'] else COLORS["danger"]
        )
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Botões
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Editar", width=90,
                                 command=lambda: self.edit_usuario(usr))
        edit_btn.pack(side="left", padx=3)
        
        if usr["ativo"]:
            status_btn = ctk.CTkButton(btn_frame, text="🚫 Desativar", width=90,
                                       fg_color=COLORS["warning"],
                                       command=lambda: self.toggle_status(usr, False))
        else:
            status_btn = ctk.CTkButton(btn_frame, text="✅ Ativar", width=90,
                                       fg_color=COLORS["success"],
                                       command=lambda: self.toggle_status(usr, True))
        status_btn.pack(side="left", padx=3)
        
        # Botão excluir permanente
        delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Excluir", width=90,
                                    fg_color=COLORS["danger"],
                                    hover_color="#a71d2a",
                                    command=lambda: self.delete_permanent(usr))
        delete_btn.pack(side="left", padx=3)
    
    def show_new_form(self):
        """Formulário novo usuário"""
        # Buscar dados FRESCOS do banco
        filiais = FilialDAO.get_all()
        
        # Validar se há filiais cadastradas
        if not filiais:
            show_error("Erro", "Não há filiais cadastradas!\nCadastre pelo menos uma filial antes de criar um usuário.")
            return
        
        dialog = FormDialog(self, "Novo Usuário", width=600, height=550)
        
        nome_entry = dialog.add_field("Nome Completo *")
        username_entry = dialog.add_field("Nome de Usuário (Login) *")
        email_entry = dialog.add_field("E-mail")
        
        perfil_combo = dialog.add_field("Perfil *", "combobox",
                                        values=list(USER_PROFILES.values()))
        perfil_combo.set(USER_PROFILES["USUARIO"])
        
        filial_combo = dialog.add_field("Filial *", "combobox",
                                        values=[f"{f['numero']} - {f['nome']}" for f in filiais])
        filial_combo.set(f"{filiais[0]['numero']} - {filiais[0]['nome']}")
        
        def save():
            nome = nome_entry.get().strip()
            username = username_entry.get().strip()
            
            if not nome or not username:
                show_error("Erro", "Nome e Username são obrigatórios!")
                return
            
            # Verificar se já existe username
            usuarios_existentes = UsuarioDAO.get_all(ativo_apenas=False)
            if any(u["username"] == username for u in usuarios_existentes):
                show_error("Erro", f"Já existe um usuário com o username '{username}'!")
                return
            
            try:
                # Obter perfil
                perfil_nome = perfil_combo.get()
                perfil = next((k for k, v in USER_PROFILES.items() if v == perfil_nome), "USUARIO")
                
                # Obter filial
                fil_numero = filial_combo.get().split(" - ")[0]
                filial = next((f for f in filiais if f["numero"] == fil_numero), None)
                
                data = {
                    "nome": nome,
                    "username": username,
                    "email": email_entry.get().strip() or None,
                    "perfil": perfil,
                    "filial_id": filial["id"]
                }
                
                UsuarioDAO.create(data)
                event_manager.emit(EVENTS['USUARIO_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Usuário cadastrado!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe um usuário com este username!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def edit_usuario(self, usr):
        """Edita usuário"""
        # Buscar dados FRESCOS do banco
        filiais = FilialDAO.get_all()
        
        # Validar se há filiais cadastradas
        if not filiais:
            show_error("Erro", "Não há filiais cadastradas!")
            return
        
        dialog = FormDialog(self, f"Editar: {usr['nome']}", width=600, height=550)
        
        nome_entry = dialog.add_field("Nome Completo *")
        nome_entry.insert(0, usr["nome"])
        
        username_label = ctk.CTkLabel(
            dialog.content_frame,
            text=f"Username: {usr['username']} (não pode ser alterado)",
            font=("Segoe UI", 10),
            text_color="#666"
        )
        username_label.pack(pady=5)
        
        email_entry = dialog.add_field("E-mail")
        if usr.get("email"):
            email_entry.insert(0, usr["email"])
        
        perfil_combo = dialog.add_field("Perfil *", "combobox",
                                        values=list(USER_PROFILES.values()))
        perfil_combo.set(USER_PROFILES[usr["perfil"]])
        
        filial_combo = dialog.add_field("Filial *", "combobox",
                                        values=[f"{f['numero']} - {f['nome']}" for f in filiais])
        
        # Selecionar filial atual
        filial_atual = next((f for f in filiais if f["id"] == usr["filial_id"]), None)
        if filial_atual:
            filial_combo.set(f"{filial_atual['numero']} - {filial_atual['nome']}")
        
        def save():
            if not nome_entry.get():
                show_error("Erro", "Nome é obrigatório!")
                return
            
            try:
                # Obter perfil
                perfil_nome = perfil_combo.get()
                perfil = next((k for k, v in USER_PROFILES.items() if v == perfil_nome), "USUARIO")
                
                # Obter filial
                fil_numero = filial_combo.get().split(" - ")[0]
                filial = next((f for f in filiais if f["numero"] == fil_numero), None)
                
                data = {
                    "nome": nome_entry.get().strip(),
                    "email": email_entry.get().strip() or None,
                    "perfil": perfil,
                    "filial_id": filial["id"]
                }
                
                UsuarioDAO.update(usr["id"], data)
                event_manager.emit(EVENTS['USUARIO_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Usuário atualizado!")
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        dialog.add_buttons(save)
    
    def toggle_status(self, usr, ativar):
        """Ativa/Desativa usuário"""
        def confirm():
            try:
                if ativar:
                    UsuarioDAO.activate(usr["id"])
                    msg = "Usuário ativado!"
                else:
                    UsuarioDAO.delete(usr["id"])
                    msg = "Usuário desativado!"
                
                event_manager.emit(EVENTS['USUARIO_CHANGED'])
                show_info("Sucesso", msg)
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        ConfirmDialog(
            self,
            "Confirmar",
            f"Deseja {'ativar' if ativar else 'desativar'} o usuário '{usr['nome']}'?",
            confirm
        )
    
    def delete_permanent(self, usr):
        """Exclui usuário permanentemente"""
        def confirm():
            try:
                from database.connection import db
                
                # Verificar se há movimentações feitas por este usuário
                check_mov = "SELECT COUNT(*) as count FROM movimentacoes WHERE usuario_id = ?"
                result_mov = db.execute_query(check_mov, (usr["id"],))
                
                # Verificar se há transferências feitas por este usuário
                check_trans = "SELECT COUNT(*) as count FROM transferencias WHERE usuario_id = ?"
                result_trans = db.execute_query(check_trans, (usr["id"],))
                
                # Verificar se há histórico de auditoria
                check_hist = "SELECT COUNT(*) as count FROM historico WHERE usuario_id = ?"
                result_hist = db.execute_query(check_hist, (usr["id"],))
                
                total_registros = result_mov[0]['count'] + result_trans[0]['count'] + result_hist[0]['count']
                
                if total_registros > 0:
                    show_error(
                        "Erro",
                        f"Não é possível excluir este usuário!\n\n"
                        f"Registros encontrados:\n"
                        f"• Movimentações: {result_mov[0]['count']}\n"
                        f"• Transferências: {result_trans[0]['count']}\n"
                        f"• Histórico: {result_hist[0]['count']}\n\n"
                        f"Usuários com histórico não podem ser excluídos.\n"
                        f"Use 'Desativar' ao invés de excluir."
                    )
                    return
                
                # Excluir permanentemente
                delete_query = "DELETE FROM usuarios WHERE id = ?"
                db.execute_update(delete_query, (usr["id"],))
                
                event_manager.emit(EVENTS['USUARIO_CHANGED'])
                show_info("Sucesso", "Usuário excluído permanentemente!")
                
            except Exception as e:
                error_msg = str(e)
                if "FOREIGN KEY constraint failed" in error_msg:
                    show_error(
                        "Erro",
                        "Não é possível excluir este usuário!\n\n"
                        "Existem registros dependentes (movimentações, transferências, etc.).\n"
                        "Usuários com histórico não podem ser excluídos."
                    )
                else:
                    show_error("Erro", f"Erro ao excluir: {error_msg}")
        
        # Confirmação única
        ConfirmDialog(
            self,
            "⚠️ ATENÇÃO - Exclusão Permanente",
            f"Deseja EXCLUIR PERMANENTEMENTE o usuário '{usr['nome']}'?\n\n" +
            "Esta ação NÃO PODE SER DESFEITA!\n\n" +
            "Recomendamos usar 'Desativar' ao invés de excluir.",
            confirm
        )

# Updated: 2025-10-14 14:28:20
