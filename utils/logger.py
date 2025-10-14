# -*- coding: utf-8 -*-
"""
Sistema de Logging Centralizado
"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Formatter com cores para o terminal"""
    
    # Códigos de cor ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Ciano
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarelo
        'ERROR': '\033[31m',      # Vermelho
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Adicionar cor ao nível
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        # Formatar mensagem
        return super().format(record)


def setup_logger(name='BrindezV2', level=logging.INFO):
    """
    Configura e retorna um logger
    
    Args:
        name: Nome do logger
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicação de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Handler para console (terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Formato com cores
    console_format = ColoredFormatter(
        '%(levelname)s | %(asctime)s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # Handler para arquivo (opcional)
    try:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f'brindez_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Arquivo guarda tudo
        
        # Formato para arquivo (sem cores)
        file_format = logging.Formatter(
            '%(levelname)s | %(asctime)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_format)
        
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Aviso: Não foi possível criar arquivo de log: {e}")
    
    logger.addHandler(console_handler)
    
    return logger


# Logger global
logger = setup_logger()


# Funções auxiliares para facilitar o uso
def debug(msg, *args, **kwargs):
    """Log de debug"""
    logger.debug(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    """Log de informação"""
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    """Log de aviso"""
    logger.warning(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    """Log de erro"""
    logger.error(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    """Log crítico"""
    logger.critical(msg, *args, **kwargs)


def exception(msg, *args, **kwargs):
    """Log de exceção (inclui traceback)"""
    logger.exception(msg, *args, **kwargs)

# Updated: 2025-10-14 14:28:20
