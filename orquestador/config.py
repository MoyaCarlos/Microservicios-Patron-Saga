"""
Configuración del orquestador
"""
import os

# Puerto del orquestador
PORT = int(os.getenv('PORT', 5000))
HOST = '0.0.0.0'
SERVICE_NAME = "orchestrator"
LOG_LEVEL = "INFO"

# URLs de los microservicios
# En Docker usar nombres de contenedores, en local usar localhost
MS_CATALOGO_URL = os.getenv('MS_CATALOGO_URL', "http://localhost:5001")
MS_COMPRAS_URL = os.getenv('MS_COMPRAS_URL', "http://localhost:5002")
MS_PAGOS_URL = os.getenv('MS_PAGOS_URL', "http://localhost:5003")
MS_INVENTARIO_URL = os.getenv('MS_INVENTARIO_URL', "http://localhost:5004")

# Mensajes
MSG_SAGA_EXITOSA = "Compra procesada exitosamente"
MSG_SAGA_FALLIDA = "Error al procesar la compra - Compensaciones ejecutadas"

# Delay entre pasos (en segundos)
DELAY_ENTRE_PASOS = 2

# Configuración de Retry
MAX_RETRIES = 3  # Número máximo de reintentos
RETRY_BASE_DELAY = 1  # Delay base en segundos para backoff exponencial

