from flask import Flask
from .resources.compras import compras_bp
from .config.config import (
    SERVICE_NAME, LOG_LEVEL, HOST, PORT
)

import logging

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    
    """
    Factory function para crear y configurar la aplicación Flask
    
    Returns:
        Instancia configurada de Flask
    """

    app = Flask(__name__)

    app.register_blueprint(compras_bp)

    logger.info(f"Aplicación {SERVICE_NAME} configurada correctamente")

    return app