from flask import Flask
from .resources.pagos import pagos_bp
from .config.config import PORT, HOST, SERVICE_NAME, LOG_LEVEL


import logging


# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    #Registrar blueprints
    app.register_blueprint(pagos_bp)
    
    logger.info(f"✅ Aplicación {SERVICE_NAME} configurada correctamente")
    
    return app


