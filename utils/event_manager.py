# -*- coding: utf-8 -*-
"""
Gerenciador de Eventos para Atualização Automática entre Telas
"""


class EventManager:
    """Gerenciador de eventos do sistema"""
    
    def __init__(self):
        self.listeners = {}
    
    def subscribe(self, event_name, callback):
        """Inscreve um callback para um evento"""
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(callback)
    
    def unsubscribe(self, event_name, callback):
        """Remove inscrição de um callback"""
        if event_name in self.listeners:
            self.listeners[event_name].remove(callback)
    
    def emit(self, event_name, data=None):
        """Emite um evento para todos os listeners"""
        if event_name in self.listeners:
            for callback in self.listeners[event_name]:
                callback(data)


# Instância global
event_manager = EventManager()

# Eventos disponíveis
EVENTS = {
    'BRINDE_CREATED': 'brinde_created',
    'BRINDE_UPDATED': 'brinde_updated',
    'BRINDE_DELETED': 'brinde_deleted',
    'STOCK_CHANGED': 'stock_changed',
    'CATEGORIA_CHANGED': 'categoria_changed',
    'UNIDADE_CHANGED': 'unidade_changed',
    'FILIAL_CHANGED': 'filial_changed',
    'USUARIO_CHANGED': 'usuario_changed',
    'FORNECEDOR_CHANGED': 'fornecedor_changed',
}

# Updated: 2025-10-14 14:28:20
