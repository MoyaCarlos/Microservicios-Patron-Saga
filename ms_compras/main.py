from .app import create_app
from .app import logger, SERVICE_NAME, HOST, PORT

app = create_app()


if __name__ == '__main__':
    
    logger.info(f"🚀 Iniciando {SERVICE_NAME} en {HOST}:{PORT}...")
    logger.info(f"✅ Servicio listo - Health check: http://localhost:{PORT}/health")
    
    app.run(host=HOST, port=PORT, debug=True)