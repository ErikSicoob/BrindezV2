# -*- coding: utf-8 -*-
"""
Tela de Configurações
"""
import customtkinter as ctk
from ui.components.form_dialog import show_info
from config.settings import COLORS


class ConfiguracoesView(ctk.CTkFrame):
    """View de configurações do sistema"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color=COLORS["content_bg"])
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Cria os widgets da tela"""
        # Container principal
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            main_container,
            text="⚙️ Configurações do Sistema",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["dark"]
        )
        title.pack(pady=(0, 20))
        
        # Abas de configuração
        self.tabview = ctk.CTkTabview(main_container, corner_radius=10)
        self.tabview.pack(fill="both", expand=True)
        
        # Criar abas
        self.tabview.add("Gerais")
        self.tabview.add("Backup")
        self.tabview.add("Fornecedores")
        self.tabview.add("Categorias")
        self.tabview.add("Unidades")
        self.tabview.add("Usuários")
        self.tabview.add("Filiais")
        
        # Conteúdo das abas
        self._create_general_tab()
        self._create_backup_tab()
        self._create_fornecedores_tab()
        self._create_categories_tab()
        self._create_units_tab()
        self._create_users_tab()
        self._create_branches_tab()
    
    def _create_general_tab(self):
        """Cria aba de configurações gerais"""
        tab = self.tabview.tab("Gerais")
        
        # Card de configurações
        card = ctk.CTkFrame(tab, fg_color="white", corner_radius=10)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Caminho do banco
        db_frame = ctk.CTkFrame(card, fg_color="transparent")
        db_frame.pack(fill="x", padx=20, pady=20)
        
        db_label = ctk.CTkLabel(
            db_frame,
            text="Caminho do Banco de Dados:",
            font=("Segoe UI", 12, "bold")
        )
        db_label.pack(anchor="w", pady=(0, 5))
        
        # Frame para entry e botão de browse
        entry_frame = ctk.CTkFrame(db_frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(0, 5))
        
        # Obter caminho atual do banco
        from config.settings import DB_PATH
        self.db_entry = ctk.CTkEntry(entry_frame, height=35)
        self.db_entry.insert(0, DB_PATH)
        self.db_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        browse_btn = ctk.CTkButton(
            entry_frame,
            text="📁 Procurar",
            height=35,
            width=100,
            command=self._browse_database_path
        )
        browse_btn.pack(side="left")
        
        # Info sobre o caminho
        info_label = ctk.CTkLabel(
            db_frame,
            text="💡 Use caminhos absolutos (ex: C:/MeusDados/brindes.db) ou relativos (ex: data/brindes.db)",
            font=("Segoe UI", 9),
            text_color="#666666",
            wraplength=600,
            justify="left"
        )
        info_label.pack(anchor="w", pady=(0, 5))
        
        db_button = ctk.CTkButton(
            db_frame,
            text="💾 Salvar Caminho do Banco",
            height=35,
            fg_color=COLORS["primary"],
            command=self._save_database_path
        )
        db_button.pack(anchor="w")
        
        # Separador
        separator = ctk.CTkFrame(card, height=2, fg_color="#e0e0e0")
        separator.pack(fill="x", padx=20, pady=20)
        
        # Estoque mínimo
        stock_frame = ctk.CTkFrame(card, fg_color="transparent")
        stock_frame.pack(fill="x", padx=20, pady=20)
        
        stock_label = ctk.CTkLabel(
            stock_frame,
            text="Quantidade Mínima para Alerta:",
            font=("Segoe UI", 12, "bold")
        )
        stock_label.pack(anchor="w", pady=(0, 5))
        
        from config.user_settings import user_settings
        self.stock_entry = ctk.CTkEntry(stock_frame, height=35, width=150)
        self.stock_entry.insert(0, str(user_settings.get_min_stock_alert()))
        self.stock_entry.pack(anchor="w")
        
        save_button = ctk.CTkButton(
            card,
            text="💾 Salvar Configurações Gerais",
            font=("Segoe UI", 14, "bold"),
            height=40,
            fg_color=COLORS["success"],
            command=self._save_general_settings
        )
        save_button.pack(padx=20, pady=(20, 20))
    
    def _create_backup_tab(self):
        """Cria aba de gerenciamento de backup"""
        tab = self.tabview.tab("Backup")
        
        # Card principal
        card = ctk.CTkFrame(tab, fg_color="white", corner_radius=10)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        title = ctk.CTkLabel(
            card,
            text="💾 Gerenciamento de Backup",
            font=("Segoe UI", 18, "bold"),
            text_color=COLORS["primary"]
        )
        title.pack(pady=(20, 10))
        
        # Informações
        info_frame = ctk.CTkFrame(card, fg_color="#e3f2fd", corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_text = ctk.CTkLabel(
            info_frame,
            text="ℹ️ O sistema mantém automaticamente apenas os 2 backups mais recentes.\nBackups são criados automaticamente a cada hora quando necessário.",
            font=("Segoe UI", 11),
            text_color="#1976d2",
            justify="center"
        )
        info_text.pack(pady=15)
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=20)
        
        # Botão criar backup
        create_btn = ctk.CTkButton(
            buttons_frame,
            text="📁 Criar Backup Agora",
            font=("Segoe UI", 12, "bold"),
            height=40,
            width=200,
            fg_color=COLORS["primary"],
            command=self._create_manual_backup
        )
        create_btn.pack(side="left", padx=(0, 10))
        
        # Botão listar backups
        list_btn = ctk.CTkButton(
            buttons_frame,
            text="📋 Ver Backups",
            font=("Segoe UI", 12, "bold"),
            height=40,
            width=150,
            fg_color=COLORS["info"],
            command=self._show_backups_list
        )
        list_btn.pack(side="left", padx=10)
        
        # Status dos backups
        self.backup_status_frame = ctk.CTkFrame(card, fg_color="#f8f9fa", corner_radius=8)
        self.backup_status_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Carregar status inicial
        self._update_backup_status()
    
    def _create_manual_backup(self):
        """Cria backup manual"""
        try:
            from database.connection import db
            from ui.components.form_dialog import show_info, show_error
            
            backup_path = db.create_backup("manual")
            if backup_path:
                show_info("Sucesso", f"Backup criado com sucesso!\n\n{backup_path}")
                self._update_backup_status()
            else:
                show_error("Erro", "Falha ao criar backup!")
        except Exception as e:
            from ui.components.form_dialog import show_error
            show_error("Erro", f"Erro ao criar backup: {str(e)}")
    
    def _show_backups_list(self):
        """Mostra lista de backups disponíveis"""
        from ui.components.form_dialog import FormDialog
        import customtkinter as ctk
        from datetime import datetime
        
        # Dialog para lista de backups
        dialog = FormDialog(self, "📋 Backups Disponíveis", width=800, height=500)
        
        # Frame para lista
        list_frame = ctk.CTkScrollableFrame(dialog.content_frame, fg_color="white", corner_radius=5)
        list_frame.pack(fill="both", expand=True, pady=10)
        
        try:
            from database.connection import db
            backups = db.list_backups()
            
            if not backups:
                no_data = ctk.CTkLabel(
                    list_frame,
                    text="Nenhum backup encontrado",
                    font=("Segoe UI", 14),
                    text_color="#999999"
                )
                no_data.pack(pady=50)
            else:
                # Cabeçalho
                header = ctk.CTkFrame(list_frame, fg_color="#e3f2fd", corner_radius=5)
                header.pack(fill="x", padx=5, pady=(5, 10))
                
                headers = ["Nome do Arquivo", "Tamanho", "Data de Criação", "Ações"]
                for i, text in enumerate(headers):
                    label = ctk.CTkLabel(header, text=text, font=("Segoe UI", 12, "bold"))
                    label.grid(row=0, column=i, padx=10, pady=10, sticky="w")
                
                # Lista de backups
                for backup in backups:
                    row = ctk.CTkFrame(list_frame, fg_color="#f8f9fa", corner_radius=3)
                    row.pack(fill="x", padx=5, pady=2)
                    
                    # Nome
                    name_label = ctk.CTkLabel(row, text=backup["filename"], font=("Segoe UI", 10))
                    name_label.grid(row=0, column=0, padx=10, pady=8, sticky="w")
                    
                    # Tamanho
                    size_mb = backup["size"] / (1024 * 1024)
                    size_label = ctk.CTkLabel(row, text=f"{size_mb:.1f} MB", font=("Segoe UI", 10))
                    size_label.grid(row=0, column=1, padx=10, pady=8, sticky="w")
                    
                    # Data
                    date_str = backup["created"].strftime("%d/%m/%Y %H:%M")
                    date_label = ctk.CTkLabel(row, text=date_str, font=("Segoe UI", 10))
                    date_label.grid(row=0, column=2, padx=10, pady=8, sticky="w")
                    
                    # Botão restaurar
                    restore_btn = ctk.CTkButton(
                        row,
                        text="🔄 Restaurar",
                        width=80,
                        height=25,
                        font=("Segoe UI", 9),
                        fg_color=COLORS["warning"],
                        command=lambda path=backup["path"]: self._restore_backup(path, dialog)
                    )
                    restore_btn.grid(row=0, column=3, padx=10, pady=8)
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                list_frame,
                text=f"Erro ao carregar backups: {str(e)}",
                font=("Segoe UI", 12),
                text_color=COLORS["danger"]
            )
            error_label.pack(pady=20)
        
        # Botão fechar
        dialog.add_buttons(lambda: dialog.safe_destroy())
    
    def _browse_database_path(self):
        """Abre diálogo para selecionar caminho do banco de dados"""
        from tkinter import filedialog
        import os
        
        # Obter diretório atual do banco
        current_path = self.db_entry.get()
        initial_dir = os.path.dirname(current_path) if current_path else os.getcwd()
        
        # Abrir diálogo
        filepath = filedialog.asksaveasfilename(
            title="Selecionar localização do Banco de Dados",
            initialdir=initial_dir,
            initialfile="brindes.db",
            defaultextension=".db",
            filetypes=[("Banco SQLite", "*.db"), ("Todos os arquivos", "*.*")]
        )
        
        if filepath:
            self.db_entry.delete(0, "end")
            self.db_entry.insert(0, filepath)
    
    def _save_database_path(self):
        """Salva novo caminho do banco de dados"""
        from ui.components.form_dialog import ConfirmDialog, show_info, show_error
        import os
        
        new_path = self.db_entry.get().strip()
        
        if not new_path:
            show_error("Erro", "Por favor, informe um caminho válido para o banco de dados!")
            return
        
        def confirm_change():
            try:
                from config.user_settings import user_settings
                
                # Salvar configuração
                if user_settings.set_db_path(new_path):
                    show_info(
                        "Sucesso",
                        f"Caminho do banco de dados atualizado!\n\n{new_path}\n\n⚠️ IMPORTANTE: Você precisa reiniciar o sistema para que a alteração tenha efeito."
                    )
                else:
                    show_error("Erro", "Falha ao salvar configuração!")
            except Exception as e:
                show_error("Erro", f"Erro ao salvar caminho do banco: {str(e)}")
        
        # Verificar se o caminho é diferente do atual
        from config.settings import DB_PATH
        if new_path == DB_PATH:
            show_info("Info", "O caminho informado já é o caminho atual do banco de dados.")
            return
        
        # Confirmar alteração
        msg = f"Deseja alterar o caminho do banco de dados?\n\n"
        msg += f"Caminho atual: {DB_PATH}\n"
        msg += f"Novo caminho: {new_path}\n\n"
        
        if os.path.exists(new_path):
            msg += "⚠️ O arquivo já existe e será utilizado.\n\n"
        else:
            msg += "⚠️ O arquivo será criado na primeira execução.\n\n"
        
        msg += "O sistema precisará ser reiniciado após a alteração."
        
        ConfirmDialog(self, "⚙️ Confirmar Alteração", msg, confirm_change)
    
    def _save_general_settings(self):
        """Salva configurações gerais"""
        from ui.components.form_dialog import show_info, show_error
        
        try:
            from config.user_settings import user_settings
            
            # Salvar quantidade mínima de estoque
            try:
                min_stock = int(self.stock_entry.get())
                if min_stock < 0:
                    raise ValueError("Quantidade deve ser positiva")
                user_settings.set_min_stock_alert(min_stock)
            except ValueError:
                show_error("Erro", "Por favor, informe um número válido para a quantidade mínima!")
                return
            
            show_info("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            show_error("Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def _restore_backup(self, backup_path, dialog):
        """Restaura um backup específico"""
        from ui.components.form_dialog import ConfirmDialog, show_info, show_error
        
        def confirm_restore():
            try:
                from database.connection import db
                success = db.restore_backup(backup_path)
                if success:
                    dialog.safe_destroy()
                    show_info("Sucesso", "Backup restaurado com sucesso!\n\nO sistema foi atualizado.")
                    self._update_backup_status()
                else:
                    show_error("Erro", "Falha ao restaurar backup!")
            except Exception as e:
                show_error("Erro", f"Erro ao restaurar backup: {str(e)}")
        
        ConfirmDialog(
            self,
            "⚠️ Confirmar Restauração",
            f"Deseja restaurar este backup?\n\n{backup_path}\n\nEsta ação irá substituir o banco atual!",
            confirm_restore
        )
    
    def _update_backup_status(self):
        """Atualiza status dos backups"""
        try:
            # Limpar frame atual
            for widget in self.backup_status_frame.winfo_children():
                widget.destroy()
            
            from database.connection import db
            backups = db.list_backups()
            
            status_label = ctk.CTkLabel(
                self.backup_status_frame,
                text=f"📊 Status: {len(backups)} backup(s) disponível(is)",
                font=("Segoe UI", 12, "bold"),
                text_color=COLORS["success"] if backups else COLORS["warning"]
            )
            status_label.pack(pady=10)
            
            if backups:
                latest = backups[0]  # Mais recente
                date_str = latest["created"].strftime("%d/%m/%Y às %H:%M")
                latest_label = ctk.CTkLabel(
                    self.backup_status_frame,
                    text=f"🕒 Último backup: {date_str}",
                    font=("Segoe UI", 10),
                    text_color="#666666"
                )
                latest_label.pack()
        
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.backup_status_frame,
                text=f"❌ Erro ao carregar status: {str(e)}",
                font=("Segoe UI", 10),
                text_color=COLORS["danger"]
            )
            error_label.pack(pady=10)
    
    def _create_fornecedores_tab(self):
        """Cria aba de fornecedores"""
        from ui.views.config.fornecedores_config import FornecedoresConfig
        
        tab = self.tabview.tab("Fornecedores")
        config = FornecedoresConfig(tab)
        config.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_categories_tab(self):
        """Cria aba de categorias"""
        from ui.views.config.categorias_config import CategoriasConfig
        
        tab = self.tabview.tab("Categorias")
        config = CategoriasConfig(tab)
        config.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_units_tab(self):
        """Cria aba de unidades"""
        from ui.views.config.unidades_config import UnidadesConfig
        
        tab = self.tabview.tab("Unidades")
        config = UnidadesConfig(tab)
        config.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_users_tab(self):
        """Cria aba de usuários"""
        from ui.views.config.usuarios_config import UsuariosConfig
        
        tab = self.tabview.tab("Usuários")
        config = UsuariosConfig(tab)
        config.pack(fill="both", expand=True, padx=20, pady=20)
    
    def _create_branches_tab(self):
        """Cria aba de filiais"""
        from ui.views.config.filiais_config import FiliaisConfig
        
        tab = self.tabview.tab("Filiais")
        config = FiliaisConfig(tab)
        config.pack(fill="both", expand=True, padx=20, pady=20)

# Updated: 2025-10-14 14:28:20
