import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Crear un formateador
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configurar el logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Configurar el handler para stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Crear un logger específico para la aplicación
    logger = logging.getLogger('crm_app')
    logger.setLevel(logging.INFO)
    
    return logger

# Crear el logger global
logger = setup_logging()