# -*- coding: utf-8 -*-
"""
Componente de Dialog para Formulários
"""
import customtkinter as ctk
from tkinter import messagebox as tk_messagebox
from config.settings import COLORS
from utils.logger import logger


# Funções auxiliares para messagebox que usam root como parent
def show_error(title, message):
    """Mostra erro de forma segura"""
    import tkinter as tk
    try:
        # Log do erro
        logger.error(f"UI Error - {title}: {message}")
        
        # Tentar obter a janela root
        root = tk._default_root
        if root:
            tk_messagebox.showerror(title, message, parent=root)
        else:
            tk_messagebox.showerror(title, message)
    except Exception as e:
        # Log do erro de path
        if "bad window path name" in str(e).lower():
            logger.error(f"BAD WINDOW PATH ERROR - {title}: {message} | Exception: {e}")
        else:
            logger.error(f"UI Exception - {title}: {message} | Exception: {e}")
        print(f"ERRO: {title} - {message}")
        print(f"Exceção: {e}")


def show_info(title, message):
    """Mostra informação de forma segura"""
    import tkinter as tk
    try:
        # Log da informação
        logger.info(f"UI Info - {title}: {message}")
        
        # Tentar obter a janela root
        root = tk._default_root
        if root:
            tk_messagebox.showinfo(title, message, parent=root)
        else:
            tk_messagebox.showinfo(title, message)
    except Exception as e:
        # Log do erro de path
        if "bad window path name" in str(e).lower():
            logger.error(f"BAD WINDOW PATH ERROR - {title}: {message} | Exception: {e}")
        else:
            logger.error(f"UI Exception - {title}: {message} | Exception: {e}")
        print(f"INFO: {title} - {message}")
        print(f"Exceção: {e}")


def show_warning(title, message):
    """Mostra aviso de forma segura"""
    import tkinter as tk
    try:
        # Log do aviso
        logger.warning(f"UI Warning - {title}: {message}")
        
        # Tentar obter a janela root
        root = tk._default_root
        if root:
            tk_messagebox.showwarning(title, message, parent=root)
        else:
            tk_messagebox.showwarning(title, message)
    except Exception as e:
        # Log do erro de path
        if "bad window path name" in str(e).lower():
            logger.error(f"BAD WINDOW PATH ERROR - {title}: {message} | Exception: {e}")
        else:
            logger.error(f"UI Exception - {title}: {message} | Exception: {e}")
        print(f"AVISO: {title} - {message}")
        print(f"Exceção: {e}")


class FormDialog(ctk.CTkToplevel):
    """Dialog base para formulários"""
    
    def __init__(self, parent, title, width=600, height=500):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.transient(parent)
        self.grab_set()
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        self.result = None
        self._is_destroyed = False
        
        # Bind do evento de fechamento
        self.protocol("WM_DELETE_WINDOW", self.safe_destroy)
        
        # Container principal
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Scrollable frame para o conteúdo
        self.content_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        # Frame de botões
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(fill="x")
    
    def safe_destroy(self):
        """Destrói o dialog de forma segura"""
        if not self._is_destroyed:
            self._is_destroyed = True
            try:
                self.grab_release()
            except:
                pass
            try:
                self.destroy()
            except:
                pass
        
    def add_field(self, label_text, widget_type="entry", **kwargs):
        """Adiciona um campo ao formulário"""
        if self._is_destroyed:
            return None
            
        field_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        field_frame.pack(fill="x", pady=10)
        
        label = ctk.CTkLabel(
            field_frame,
            text=label_text,
            font=("Segoe UI", 12, "bold"),
            anchor="w"
        )
        label.pack(fill="x", pady=(0, 5))
        
        if widget_type == "entry":
            widget = ctk.CTkEntry(field_frame, height=35, **kwargs)
        elif widget_type == "textbox":
            widget = ctk.CTkTextbox(field_frame, height=80, **kwargs)
        elif widget_type == "combobox":
            # Remover command se existir para evitar problemas
            kwargs_copy = kwargs.copy()
            if 'command' in kwargs_copy:
                del kwargs_copy['command']
            widget = ctk.CTkComboBox(field_frame, height=35, state="readonly", **kwargs_copy)
        elif widget_type == "checkbox":
            widget = ctk.CTkCheckBox(field_frame, text="", **kwargs)
        else:
            widget = ctk.CTkEntry(field_frame, height=35, **kwargs)
        
        widget.pack(fill="x")
        
        return widget
    
    def add_buttons(self, on_save, on_cancel=None):
        """Adiciona botões de ação"""
        cancel_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Cancelar",
            font=("Segoe UI", 14),
            height=40,
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=on_cancel or self.safe_destroy
        )
        cancel_btn.pack(side="right", padx=5)
        
        save_btn = ctk.CTkButton(
            self.buttons_frame,
            text="Salvar",
            font=("Segoe UI", 14, "bold"),
            height=40,
            fg_color=COLORS["success"],
            hover_color="#218838",
            command=on_save
        )
        save_btn.pack(side="right", padx=5)


class ConfirmDialog(ctk.CTkToplevel):
    """Dialog de confirmação"""
    
    def __init__(self, parent, title, message, on_confirm):
        super().__init__(parent)
        
        self.title(title)
        # Tamanho maior e fixo para garantir que os botões apareçam
        self.geometry("550x350")
        self.resizable(False, False)  # Não permite redimensionar
        self.transient(parent)
        self.grab_set()
        
        self._is_destroyed = False
        self.protocol("WM_DELETE_WINDOW", self.safe_destroy)
        
        # Centralizar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (275)  # 550/2
        y = (self.winfo_screenheight() // 2) - (175)  # 350/2
        self.geometry(f"+{x}+{y}")
        
        # Container principal com padding
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mensagem com scroll se necessário
        msg_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        msg_frame.pack(fill="both", expand=True, pady=(0, 20))
        
        msg_label = ctk.CTkLabel(
            msg_frame,
            text=message,
            font=("Segoe UI", 13),
            wraplength=500,
            justify="left"
        )
        msg_label.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Botões fixos na parte inferior - centralizados
        buttons_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        buttons_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # Container interno para centralizar os botões
        buttons_inner = ctk.CTkFrame(buttons_frame, fg_color="transparent")
        buttons_inner.pack(expand=True)
        
        cancel_btn = ctk.CTkButton(
            buttons_inner,
            text="Cancelar",
            width=140,
            height=45,
            font=("Segoe UI", 14),
            fg_color="#6c757d",
            hover_color="#5a6268",
            command=self.safe_destroy
        )
        cancel_btn.pack(side="left", padx=15)
        
        confirm_btn = ctk.CTkButton(
            buttons_inner,
            text="Confirmar",
            width=140,
            height=45,
            font=("Segoe UI", 14, "bold"),
            fg_color=COLORS["danger"],
            hover_color="#c82333",
            command=lambda: self._on_confirm(on_confirm)
        )
        confirm_btn.pack(side="left", padx=15)
    
    def safe_destroy(self):
        """Destrói o dialog de forma segura"""
        if not self._is_destroyed:
            self._is_destroyed = True
            try:
                logger.debug(f"Destruindo dialog: {self.title()}")
                self.grab_release()
            except Exception as e:
                if "bad window path name" in str(e).lower():
                    logger.error(f"BAD WINDOW PATH ERROR em grab_release: {e}")
                else:
                    logger.debug(f"Erro em grab_release (normal): {e}")
            try:
                self.destroy()
                logger.debug(f"Dialog destruído com sucesso")
            except Exception as e:
                if "bad window path name" in str(e).lower():
                    logger.error(f"BAD WINDOW PATH ERROR em destroy: {e}")
                else:
                    logger.debug(f"Erro em destroy (normal): {e}")
    
    def _on_confirm(self, callback):
        """Executa callback e fecha"""
        if not self._is_destroyed:
            self._is_destroyed = True
            
            # Salvar referência ao root antes de destruir
            try:
                root = self.winfo_toplevel()
            except:
                root = None
            
            # Liberar grab
            try:
                self.grab_release()
            except:
                pass
            
            # Destruir imediatamente
            try:
                self.destroy()
                logger.debug("ConfirmDialog destruído com sucesso")
            except Exception as e:
                if "bad window path name" in str(e).lower():
                    logger.error(f"BAD WINDOW PATH ERROR em ConfirmDialog destroy: {e}")
                else:
                    logger.debug(f"Erro em ConfirmDialog destroy (normal): {e}")
            
            # Executar callback após destruição completa
            def execute_callback():
                try:
                    logger.debug("Executando callback do ConfirmDialog")
                    callback()
                except Exception as e:
                    if "bad window path name" in str(e).lower():
                        logger.error(f"BAD WINDOW PATH ERROR no callback: {e}")
                    else:
                        logger.error(f"Erro no callback do ConfirmDialog: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Aguardar um pouco mais para garantir destruição completa
            try:
                if root and hasattr(root, 'after'):
                    root.after(350, execute_callback)
                else:
                    import threading
                    timer = threading.Timer(0.35, execute_callback)
                    timer.start()
            except:
                execute_callback()

# Updated: 2025-10-14 14:28:20
