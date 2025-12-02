#Configuración del microservicio de compras

# Puerto del servicio
PORT = 5002
HOST = '0.0.0.0'

# Nombre del servicio
SERVICE_NAME = "ms-compras"

# Configuración de logging
LOG_LEVEL = "INFO"

# Mensajes estandarizados
MSG_COMPRA_EXITOSA = "Compra registrada exitosamente"
MSG_COMPRA_FALLIDA = "No se pudo registrar la compra"
MSG_COMPRA_CANCELADA = "Compra cancelada"
MSG_NO_COMPRA_COMPENSAR = "No hay compra para compensar"

# Estados de compra
ESTADO_CONFIRMADA = "confirmada"
ESTADO_CANCELADA = "cancelada"

# Probabilidad de éxito (0.0 a 1.0)
PROBABILIDAD_EXITO = 0.5