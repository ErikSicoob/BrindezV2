# -*- coding: utf-8 -*-
"""
Configuração de Categorias
"""
import customtkinter as ctk
from config.settings import COLORS
from database.dao import CategoriaDAO
from ui.components.form_dialog import FormDialog, ConfirmDialog, show_error, show_info, show_warning
from utils.event_manager import event_manager, EVENTS
from utils.auth import auth_manager

class CategoriasConfig(ctk.CTkFrame):
    """Configuração de Categorias"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self._create_widgets()
        self.load_data()
        
        event_manager.subscribe(EVENTS['CATEGORIA_CHANGED'], lambda d: self._safe_reload())
    
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
            text="➕ Nova Categoria",
            font=("Segoe UI", 14, "bold"),
            height=40,
            fg_color=COLORS["primary"],
            command=self.show_new_form
        )
        new_btn.pack(pady=(0, 20))
        
        # Lista
        self.list_frame = ctk.CTkScrollableFrame(self, fg_color=COLORS["card_bg"], corner_radius=10)
        self.list_frame.pack(fill="both", expand=True)
    
    def load_data(self):
        """Carrega categorias"""
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
        
        categorias = CategoriaDAO.get_all(ativo_apenas=False)
        
        if not categorias:
            no_data = ctk.CTkLabel(
                self.list_frame,
                text="Nenhuma categoria cadastrada",
                font=("Segoe UI", 14),
                text_color="#999999"
            )
            no_data.pack(pady=50)
        else:
            for cat in categorias:
                self._create_row(cat)
    
    def _create_row(self, cat):
        """Cria linha de categoria"""
        row = ctk.CTkFrame(self.list_frame, fg_color="#f8f9fa", corner_radius=5)
        row.pack(fill="x", padx=10, pady=5)
        
        # Info
        info_frame = ctk.CTkFrame(row, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
        
        name_label = ctk.CTkLabel(info_frame, text=cat["nome"], 
                                  font=("Segoe UI", 14, "bold"))
        name_label.pack(anchor="w")
        
        if cat.get("descricao"):
            desc_label = ctk.CTkLabel(info_frame, text=cat["descricao"], 
                                     font=("Segoe UI", 10), text_color="#666")
            desc_label.pack(anchor="w")
        
        # Status
        status_label = ctk.CTkLabel(
            info_frame,
            text=f"Status: {'✅ Ativo' if cat['ativo'] else '🚫 Inativo'}",
            font=("Segoe UI", 9),
            text_color=COLORS["success"] if cat['ativo'] else COLORS["danger"]
        )
        status_label.pack(anchor="w", pady=(5, 0))
        
        # Botões
        btn_frame = ctk.CTkFrame(row, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)
        
        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Editar", width=90,
                                 command=lambda: self.edit(cat))
        edit_btn.pack(side="left", padx=3)
        
        # Apenas ADMIN pode desativar/excluir
        from utils.auth import auth_manager
        if auth_manager.has_permission("admin"):
            if cat["ativo"]:
                status_btn = ctk.CTkButton(btn_frame, text="🚫 Desativar", width=90,
                                           fg_color=COLORS["warning"],
                                           command=lambda: self.toggle_status(cat, False))
            else:
                status_btn = ctk.CTkButton(btn_frame, text="✅ Ativar", width=90,
                                           fg_color=COLORS["success"],
                                           command=lambda: self.toggle_status(cat, True))
            status_btn.pack(side="left", padx=3)
            
            # Botão excluir permanente
            delete_btn = ctk.CTkButton(btn_frame, text="🗑️ Excluir", width=90,
                                        fg_color=COLORS["danger"],
                                        hover_color="#a71d2a",
                                        command=lambda: self.delete_permanent(cat))
            delete_btn.pack(side="left", padx=3)
    
    def show_new_form(self):
        """Formulário nova categoria"""
        dialog = FormDialog(self, "Nova Categoria", width=500, height=350)
        
        nome_entry = dialog.add_field("Nome *")
        desc_text = dialog.add_field("Descrição", "textbox")
        
        def save():
            nome = nome_entry.get().strip()
            if not nome:
                show_error("Erro", "Nome é obrigatório!")
                return
            
            # Verificar se já existe
            categorias_existentes = CategoriaDAO.get_all(ativo_apenas=False)
            if any(c["nome"].lower() == nome.lower() for c in categorias_existentes):
                show_error("Erro", f"Já existe uma categoria com o nome '{nome}'!")
                return
            
            try:
                data = {
                    "nome": nome,
                    "descricao": desc_text.get("1.0", "end-1c").strip() or None
                }
                
                CategoriaDAO.create(data)
                event_manager.emit(EVENTS['CATEGORIA_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Categoria cadastrada!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe uma categoria com este nome!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def edit(self, cat):
        """Edita categoria"""
        dialog = FormDialog(self, f"Editar: {cat['nome']}", width=500, height=350)
        
        nome_entry = dialog.add_field("Nome *")
        nome_entry.insert(0, cat["nome"])
        
        desc_text = dialog.add_field("Descrição", "textbox")
        if cat.get("descricao"):
            desc_text.insert("1.0", cat["descricao"])
        
        def save():
            nome = nome_entry.get().strip()
            if not nome:
                show_error("Erro", "Nome é obrigatório!")
                return
            
            # Verificar se já existe (exceto a própria categoria)
            categorias_existentes = CategoriaDAO.get_all(ativo_apenas=False)
            if any(c["nome"].lower() == nome.lower() and c["id"] != cat["id"] for c in categorias_existentes):
                show_error("Erro", f"Já existe outra categoria com o nome '{nome}'!")
                return
            
            try:
                data = {
                    "nome": nome,
                    "descricao": desc_text.get("1.0", "end-1c").strip() or None
                }
                
                CategoriaDAO.update(cat["id"], data)
                event_manager.emit(EVENTS['CATEGORIA_CHANGED'])
                dialog.safe_destroy()
                show_info("Sucesso", "Categoria atualizada!")
                
            except Exception as e:
                error_msg = str(e)
                if "UNIQUE constraint failed" in error_msg:
                    show_error("Erro", "Já existe uma categoria com este nome!")
                else:
                    show_error("Erro", f"Erro: {error_msg}")
        
        dialog.add_buttons(save)
    
    def toggle_status(self, cat, ativar):
        """Ativa/Desativa categoria"""
        def confirm():
            try:
                if not ativar:
                    # Verificar se há brindes usando esta categoria
                    from database.dao import BrindeDAO
                    brindes = BrindeDAO.get_by_category(cat["id"])
                    if brindes:
                        show_error(
                            "Erro",
                            f"Não é possível desativar!\nExistem {len(brindes)} brindes usando esta categoria."
                        )
                        return
                
                if ativar:
                    CategoriaDAO.activate(cat["id"])
                    msg = "Categoria ativada!"
                else:
                    CategoriaDAO.delete(cat["id"])
                    msg = "Categoria desativada!"
                
                event_manager.emit(EVENTS['CATEGORIA_CHANGED'])
                show_info("Sucesso", msg)
                
            except Exception as e:
                show_error("Erro", f"Erro: {str(e)}")
        
        ConfirmDialog(
            self,
            "Confirmar",
            f"Deseja {'ativar' if ativar else 'desativar'} a categoria '{cat['nome']}'?",
            confirm
        )
    
    def delete_permanent(self, cat):
        """Exclui categoria permanentemente"""
        def confirm():
            try:
                # Verificar se há brindes usando esta categoria
                from database.dao import BrindeDAO
                brindes = BrindeDAO.get_by_category(cat["id"])
                if brindes:
                    show_error(
                        "Erro",
                        f"Não é possível excluir!\nExistem {len(brindes)} brindes usando esta categoria.\n\nDesative a categoria ao invés de excluir."
                    )
                    return
                
                # Excluir permanentemente
                from database.connection import db
                delete_query = "DELETE FROM categorias WHERE id = ?"
                db.execute_update(delete_query, (cat["id"],))
                
                event_manager.emit(EVENTS['CATEGORIA_CHANGED'])
                show_info("Sucesso", "Categoria excluída permanentemente!")
                
            except Exception as e:
                show_error("Erro", f"Erro ao excluir: {str(e)}")
        
        # Confirmação única
        ConfirmDialog(
            self,
            "⚠️ ATENÇÃO - Exclusão Permanente",
            f"Deseja EXCLUIR PERMANENTEMENTE a categoria '{cat['nome']}'?\n\n" +
            "Esta ação NÃO PODE SER DESFEITA!\n\n" +
            "Recomendamos usar 'Desativar' ao invés de excluir.",
            confirm
        )

# Updated: 2025-10-14 14:28:20
