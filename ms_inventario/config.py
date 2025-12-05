"""
Configuración del microservicio de inventario
"""

# Puerto del servicio
PORT = 5004
HOST = '0.0.0.0'

# Nombre del servicio
SERVICE_NAME = "ms-inventario"

# Configuración de logging
LOG_LEVEL = "INFO"

# Mensajes estandarizados
MSG_RESERVA_EXITOSA = "Stock reservado exitosamente"
MSG_PRODUCTO_NO_ENCONTRADO = "Producto no encontrado"
MSG_STOCK_INSUFICIENTE = "Stock insuficiente"
MSG_RESERVA_COMPENSADA = "Reserva compensada exitosamente"
MSG_NO_RESERVA_COMPENSAR = "No hay reserva para compensar"

# Estados de reserva
ESTADO_RESERVADO = "reservado"
ESTADO_CANCELADA = "cancelada"

# Inventario inicial
INVENTARIO_INICIAL = {
    "LAPTOP": {"stock": 5, "reservado": 0},
    "MOUSE": {"stock": 10, "reservado": 0},
    "TECLADO": {"stock": 3, "reservado": 0},
    "AURICULARES": {"stock": 15, "reservado": 0},
    "MONITOR": {"stock": 8, "reservado": 0}
}