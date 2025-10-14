# -*- coding: utf-8 -*-
"""
Utilitários de logging específicos para UI
"""
from utils.logger import logger
import functools
import traceback


def log_ui_errors(func):
    """
    Decorator para capturar e logar erros de UI, especialmente "bad window path name"
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e).lower()
            func_name = func.__name__
            
            if "bad window path name" in error_msg:
                logger.error(f"BAD WINDOW PATH ERROR em {func_name}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            elif "invalid command name" in error_msg:
                logger.error(f"INVALID COMMAND ERROR em {func_name}: {e}")
                logger.error(f"Traceback: {traceback.format_exc()}")
            else:
                logger.error(f"UI Error em {func_name}: {e}")
                logger.debug(f"Traceback: {traceback.format_exc()}")
            
            # Re-raise a exceção para não quebrar o fluxo
            raise
    
    return wrapper


def safe_ui_call(func, *args, **kwargs):
    """
    Executa uma função de UI de forma segura, logando erros de path
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_msg = str(e).lower()
        func_name = getattr(func, '__name__', 'unknown_function')
        
        if "bad window path name" in error_msg:
            logger.error(f"BAD WINDOW PATH ERROR em {func_name}: {e}")
        elif "invalid command name" in error_msg:
            logger.error(f"INVALID COMMAND ERROR em {func_name}: {e}")
        else:
            logger.error(f"UI Error em {func_name}: {e}")
        
        # Não re-raise para não quebrar o fluxo
        return None


def log_widget_operation(operation, widget_info=""):
    """
    Loga operações em widgets para debug
    """
    logger.debug(f"Widget Operation: {operation} | {widget_info}")

# Updated: 2025-10-14 14:28:20
