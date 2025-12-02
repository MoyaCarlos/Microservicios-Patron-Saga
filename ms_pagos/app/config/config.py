#Configuracion para microservicio de pagos

# Puerto del servicio
PORT = 5003
HOST = '0.0.0.0'

# Nombre del servicio
SERVICE_NAME = "ms-pagos"

# Configuración de logging
LOG_LEVEL = "INFO"

# Mensajes estandarizados
MSG_PAGO_EXITOSO = "Pago procesado exitosamente"
MSG_PAGO_FALLIDO = "No se pudo procesar el pago"
MSG_PAGO_REEMBOLSADO = "Pago reembolsado"
MSG_NO_PAGO_COMPENSAR = "No hay pago para compensar"

# Estados de pago
ESTADO_APROBADO = "aprobado"
ESTADO_REEMBOLSADO = "reembolsado"

# Probabilidad de éxito (0.0 a 1.0)
PROBABILIDAD_EXITO = 0.5