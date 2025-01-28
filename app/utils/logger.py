import logging
import sys

def get_logger():
    # Crear logger
    logger = logging.getLogger('crm_app')
    logger.setLevel(logging.INFO)

    # Evitar duplicación de handlers
    if not logger.handlers:
        # Crear handler para stdout
        handler = logging.StreamHandler(sys.stdout)
        
        # Crear formatter
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Añadir formatter al handler
        handler.setFormatter(formatter)
        
        # Añadir handler al logger
        logger.addHandler(handler)

    return logger

# Crear logger global
logger = get_logger()