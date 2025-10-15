# -*- coding: utf-8 -*-
"""
Componente de Menu de Contexto
Menu que aparece ao clicar com botão direito
"""
import customtkinter as ctk
from config.settings import COLORS


class ContextMenu(ctk.CTkToplevel):
    """Menu de contexto personalizado"""
    
    def __init__(self, master, x, y, items, **kwargs):
        """
        Args:
            master: Widget pai
            x, y: Coordenadas para exibir o menu
            items: Lista de dicts com {'label': str, 'command': callable, 'color': str (opcional)}
        """
        super().__init__(master, **kwargs)
        
        # Configurar janela
        self.overrideredirect(True)  # Remover decorações
        self.configure(fg_color="white", border_width=1, border_color="#cccccc")
        
        # Posicionar
        self.geometry(f"+{x}+{y}")
        
        # Criar itens do menu
        for item in items:
            if item.get('separator'):
                # Separador
                sep = ctk.CTkFrame(self, height=1, fg_color="#e0e0e0")
                sep.pack(fill="x", padx=5, pady=3)
            else:
                # Item do menu
                btn = ctk.CTkButton(
                    self,
                    text=item['label'],
                    fg_color="transparent",
                    hover_color="#f0f0f0",
                    text_color=item.get('color', COLORS["dark"]),
                    anchor="w",
                    height=32,
                    corner_radius=0,
                    font=("Segoe UI", 11),
                    command=lambda cmd=item['command']: self._execute_and_close(cmd)
                )
                btn.pack(fill="x", padx=2, pady=1)
        
        # Fechar ao clicar fora
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.focus_force()
        
        # Ajustar largura mínima
        self.update_idletasks()
        width = max(180, self.winfo_reqwidth())
        self.geometry(f"{width}x{self.winfo_reqheight()}")
    
    def _execute_and_close(self, command):
        """Executa comando e fecha o menu"""
        self.destroy()
        if command:
            command()


def show_context_menu(widget, event, items):
    """
    Mostra menu de contexto
    
    Args:
        widget: Widget que recebeu o evento
        event: Evento do clique direito
        items: Lista de itens do menu
    """
    # Calcular posição absoluta
    x = widget.winfo_rootx() + event.x
    y = widget.winfo_rooty() + event.y
    
    # Criar e mostrar menu
    menu = ContextMenu(widget, x, y, items)
    menu.lift()
