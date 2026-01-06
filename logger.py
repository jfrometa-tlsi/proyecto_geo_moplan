import logging
import os

def setup_logger(name:str) -> logging.Logger:
    """Configurar el sistema de logging"""
    
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Nombre del archivo con fecha
    log_filename = "logs/logs.log"
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # También muestra en consola
        ]
    )    
    return logging.getLogger(name)

