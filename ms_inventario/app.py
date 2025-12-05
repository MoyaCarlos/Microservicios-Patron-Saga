from flask import Flask
import logging

from .routes import inventario_bp
from .config import PORT, HOST, SERVICE_NAME, LOG_LEVEL

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
    
    # Registrar blueprints
    app.register_blueprint(inventario_bp)
    
    logger.info(f"✅ Aplicación {SERVICE_NAME} configurada correctamente")
    
    return app


# Exportar app para Granian
app = create_app()


if __name__ == '__main__':
    
    logger.info(f"🚀 Iniciando {SERVICE_NAME} en {HOST}:{PORT}...")
    logger.info(f"✅ Servicio listo - Health check: http://localhost:{PORT}/health")
    
    app.run(host=HOST, port=PORT, debug=True)