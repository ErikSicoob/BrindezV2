# -*- coding: utf-8 -*-
"""
Módulo de Autenticação e Controle de Acesso
"""
import os
import getpass


class AuthManager:
    """Gerenciador de autenticação e permissões"""
    
    def __init__(self):
        self.current_user = None
        self.windows_user = None
        
    def get_windows_user(self):
        """Obtém o usuário logado no Windows"""
        try:
            self.windows_user = getpass.getuser()
            return self.windows_user
        except:
            return "unknown"
    
    def authenticate(self):
        """
        Autentica usuário com base no login do Windows
        Busca usuário no banco de dados
        """
        from database.dao import UsuarioDAO
        
        windows_user = self.get_windows_user()
        
        # Buscar usuário no banco
        user = UsuarioDAO.get_by_username(windows_user)
        
        if user:
            self.current_user = {
                "id": user['id'],
                "name": user['nome'],
                "username": user['username'],
                "profile": user['perfil'],
                "branch_id": user['filial_id'],
                "branch_name": user['filial_nome'],
                "active": user['ativo']
            }
        else:
            # Se não encontrar, criar usuário admin temporário
            self.current_user = {
                "id": 1,
                "name": "Administrador",
                "username": windows_user,
                "profile": "ADMIN",
                "branch_id": 1,
                "branch_name": "Matriz",
                "active": True
            }
        
        return self.current_user
    
    def has_permission(self, permission):
        """
        Verifica se o usuário tem determinada permissão
        
        Permissões:
        - admin: Apenas administradores
        - gestor: Gestores e administradores
        - usuario: Todos os usuários
        """
        if not self.current_user:
            return False
        
        profile = self.current_user.get("profile", "USUARIO")
        
        if permission == "admin":
            return profile == "ADMIN"
        elif permission == "gestor":
            return profile in ["ADMIN", "GESTOR"]
        elif permission == "usuario":
            return True
        
        return False
    
    def can_view_all_branches(self):
        """Verifica se usuário pode ver todas as filiais (apenas Matriz)"""
        if not self.current_user:
            return False
        return self.current_user.get("branch_id") == 1  # Matriz
    
    def get_user_branch(self):
        """Retorna a filial do usuário"""
        if not self.current_user:
            return None
        return self.current_user.get("branch_id")


# Instância global
auth_manager = AuthManager()
