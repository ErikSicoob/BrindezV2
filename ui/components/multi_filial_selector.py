# -*- coding: utf-8 -*-
"""
Componente de Seleção de Múltiplas Filiais
Permite distribuir quantidade de brindes entre filiais
"""
import customtkinter as ctk
from config.settings import COLORS


class MultiFilialSelector(ctk.CTkFrame):
    """Seletor de múltiplas filiais com distribuição de quantidades"""
    
    def __init__(self, master, filiais, quantidade_total_callback, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        self.filiais = filiais
        self.quantidade_total_callback = quantidade_total_callback
        self.modo_multiplo = ctk.BooleanVar(value=False)
        self.filial_entries = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets do seletor"""
        # Checkbox para modo múltiplo
        checkbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        checkbox_frame.pack(fill="x", pady=(0, 10))
        
        self.checkbox = ctk.CTkCheckBox(
            checkbox_frame,
            text="Distribuir entre múltiplas filiais",
            variable=self.modo_multiplo,
            command=self._toggle_modo,
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["primary"]
        )
        self.checkbox.pack(anchor="w")
        
        # Frame para filial única
        self.single_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.single_frame.pack(fill="x")
        
        single_label = ctk.CTkLabel(
            self.single_frame,
            text="Filial:",
            font=("Segoe UI", 11, "bold")
        )
        single_label.pack(anchor="w", pady=(0, 5))
        
        self.single_combo = ctk.CTkComboBox(
            self.single_frame,
            values=[f"{f['numero']} - {f['nome']}" for f in self.filiais],
            width=400
        )
        self.single_combo.pack(anchor="w")
        if self.filiais:
            self.single_combo.set(f"{self.filiais[0]['numero']} - {self.filiais[0]['nome']}")
        
        # Frame para múltiplas filiais com scroll bloqueado
        self.multi_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS["light"],
            corner_radius=8,
            height=250,
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_light"]
        )
        
        # Bloquear propagação de eventos de scroll
        self._setup_scroll_blocking()
        
        self._create_multi_filial_widgets()
    
    def _setup_scroll_blocking(self):
        """Configura bloqueio de scroll do pai quando mouse sobre o frame"""
        self._mouse_over_box = False
        
        # Detectar quando mouse está sobre a box
        self.multi_frame.bind("<Enter>", lambda e: setattr(self, '_mouse_over_box', True))
        self.multi_frame.bind("<Leave>", lambda e: setattr(self, '_mouse_over_box', False))
        
        # Aguardar um pouco para garantir que o widget foi criado
        self.after(200, self._apply_scroll_intercept)
    
    def _apply_scroll_intercept(self):
        """Aplica interceptação de scroll"""
        try:
            # Pegar o content_frame do dialog (que é scrollable)
            toplevel = self.winfo_toplevel()
            
            # Procurar pelo CTkScrollableFrame do dialog
            for child in toplevel.winfo_children():
                if hasattr(child, '_parent_canvas') and hasattr(child, '_on_mouse_wheel'):
                    # Encontrou o scrollable frame do modal
                    canvas = child._parent_canvas
                    original_handler = child._on_mouse_wheel
                    
                    # Criar wrapper que verifica se mouse está sobre a box
                    def scroll_wrapper(event, original=original_handler):
                        # Se mouse está sobre a box, não scrollar o modal
                        if hasattr(self, '_mouse_over_box') and self._mouse_over_box:
                            return "break"
                        # Caso contrário, executar scroll normal
                        return original(event)
                    
                    # Substituir o handler
                    canvas.bind("<MouseWheel>", scroll_wrapper)
                    canvas.bind("<Button-4>", scroll_wrapper)
                    canvas.bind("<Button-5>", scroll_wrapper)
                    break
        except Exception as e:
            pass
    
    def _create_multi_filial_widgets(self):
        """Cria widgets para seleção de múltiplas filiais"""
        # Limpar frame
        for widget in self.multi_frame.winfo_children():
            widget.destroy()
        
        # Info
        info_label = ctk.CTkLabel(
            self.multi_frame,
            text="💡 Informe a quantidade para cada filial. A soma deve ser igual à quantidade total informada.",
            font=("Segoe UI", 10),
            text_color="#666666",
            wraplength=600,
            justify="left"
        )
        info_label.pack(anchor="w", padx=10, pady=(10, 15))
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(self.multi_frame, fg_color=COLORS["primary"], corner_radius=5)
        header_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        filial_header = ctk.CTkLabel(
            header_frame,
            text="Filial",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["white"],
            width=300,
            anchor="w"
        )
        filial_header.pack(side="left", padx=10, pady=8)
        
        qty_header = ctk.CTkLabel(
            header_frame,
            text="Quantidade",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["white"],
            width=150,
            anchor="w"
        )
        qty_header.pack(side="left", padx=10, pady=8)
        
        # Lista de filiais
        self.filial_entries = {}
        for filial in self.filiais:
            row_frame = ctk.CTkFrame(self.multi_frame, fg_color=COLORS["card_bg"], corner_radius=3)
            row_frame.pack(fill="x", padx=10, pady=5)
            
            # Nome da filial
            filial_label = ctk.CTkLabel(
                row_frame,
                text=f"{filial['numero']} - {filial['nome']} ({filial['cidade']})",
                font=("Segoe UI", 10),
                width=300,
                anchor="w"
            )
            filial_label.pack(side="left", padx=10, pady=8)
            
            # Entry para quantidade
            qty_entry = ctk.CTkEntry(
                row_frame,
                width=150,
                placeholder_text="0"
            )
            qty_entry.insert(0, "0")
            qty_entry.pack(side="left", padx=10, pady=8)
            
            # Vincular evento de mudança
            qty_entry.bind("<KeyRelease>", lambda e: self._update_total())
            
            # Permitir apenas números
            def validate_number(event, entry=qty_entry):
                value = entry.get()
                # Remover caracteres não numéricos
                filtered = ''.join(filter(str.isdigit, value))
                if filtered != value:
                    entry.delete(0, "end")
                    entry.insert(0, filtered)
                self._update_total()
            
            qty_entry.bind("<KeyRelease>", validate_number)
            
            self.filial_entries[filial['id']] = qty_entry
        
        # Label de total
        total_frame = ctk.CTkFrame(self.multi_frame, fg_color=COLORS["hover"], corner_radius=5)
        total_frame.pack(fill="x", padx=10, pady=(15, 10))
        
        self.total_label = ctk.CTkLabel(
            total_frame,
            text="Total distribuído: 0",
            font=("Segoe UI", 11, "bold"),
            text_color=COLORS["primary"]
        )
        self.total_label.pack(pady=10)
        
        self.validation_label = ctk.CTkLabel(
            total_frame,
            text="",
            font=("Segoe UI", 10),
            text_color=COLORS["danger"]
        )
        self.validation_label.pack(pady=(0, 10))
    
    def _toggle_modo(self):
        """Alterna entre modo único e múltiplo"""
        if self.modo_multiplo.get():
            self.single_frame.pack_forget()
            self.multi_frame.pack(fill="both", expand=True, pady=(10, 0))
            self._update_total()
        else:
            self.multi_frame.pack_forget()
            self.single_frame.pack(fill="x")
    
    def _update_total(self):
        """Atualiza o total distribuído"""
        if not self.modo_multiplo.get():
            return
        
        total = 0
        for entry in self.filial_entries.values():
            try:
                value = int(entry.get() or 0)
                total += value
            except ValueError:
                pass
        
        self.total_label.configure(text=f"Total distribuído: {total}")
        
        # Validar contra quantidade total
        try:
            quantidade_total = int(self.quantidade_total_callback())
            if total > quantidade_total:
                self.validation_label.configure(
                    text=f"⚠️ Total distribuído ({total}) excede a quantidade total ({quantidade_total})!",
                    text_color=COLORS["danger"]
                )
            elif total < quantidade_total and total > 0:
                diff = quantidade_total - total
                self.validation_label.configure(
                    text=f"⚠️ Faltam {diff} unidades para atingir o total ({quantidade_total})",
                    text_color=COLORS["warning"]
                )
            elif total == quantidade_total:
                self.validation_label.configure(
                    text="✓ Quantidade corretamente distribuída!",
                    text_color=COLORS["success"]
                )
            else:
                self.validation_label.configure(text="")
        except (ValueError, TypeError):
            self.validation_label.configure(text="")
    
    def get_distribuicao(self):
        """Retorna a distribuição de quantidades por filial"""
        if not self.modo_multiplo.get():
            # Modo único - retornar filial selecionada
            fil_str = self.single_combo.get()
            fil_numero = fil_str.split(" - ")[0]
            filial = next((f for f in self.filiais if f["numero"] == fil_numero), None)
            if filial:
                return {filial['id']: None}  # None significa usar a quantidade total
            return {}
        else:
            # Modo múltiplo - retornar distribuição
            distribuicao = {}
            for filial_id, entry in self.filial_entries.items():
                try:
                    qty = int(entry.get() or 0)
                    if qty > 0:
                        distribuicao[filial_id] = qty
                except ValueError:
                    pass
            return distribuicao
    
    def validate(self, quantidade_total):
        """Valida a distribuição contra a quantidade total"""
        distribuicao = self.get_distribuicao()
        
        if not distribuicao:
            return False, "Nenhuma filial selecionada!"
        
        if not self.modo_multiplo.get():
            # Modo único - sempre válido
            return True, ""
        
        # Modo múltiplo - verificar soma
        total = sum(distribuicao.values())
        
        if total != quantidade_total:
            return False, f"A soma das quantidades ({total}) deve ser igual à quantidade total ({quantidade_total})!"
        
        return True, ""
