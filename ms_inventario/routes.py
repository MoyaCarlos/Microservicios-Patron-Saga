"""
Definición de rutas/endpoints para el microservicio de inventario
"""
from flask import Blueprint, jsonify, request
from typing import Tuple
from .services.inventario_service import InventarioService
from .config import SERVICE_NAME

# Crear blueprint para las rutas
inventario_bp = Blueprint('inventario', __name__)

# Instancia única del servicio (Singleton pattern)
inventario_service = InventarioService()


@inventario_bp.route("/health", methods=["GET"])
def health() -> Tuple[dict, int]:
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@inventario_bp.route("/inventario", methods=["GET"])
def obtener_inventario() -> Tuple[dict, int]:
    """
    Endpoint para obtener el estado actual del inventario.
    
    Returns:
        200: Estado del inventario
    """
    response, status_code = inventario_service.obtener_inventario()
    return jsonify(response), status_code


@inventario_bp.route("/transaccion", methods=["POST"])
def reservar_stock() -> Tuple[dict, int]:
    """
    Endpoint para reservar stock de un producto.
    
    Request body:
        {
            "producto": str,
            "cantidad": int (opcional, default: 1)
        }
    
    Returns:
        200: Reserva exitosa
        409: Producto no encontrado o stock insuficiente
    """
    data = request.get_json()
    # Aceptar tanto 'producto' como 'producto_id'
    producto = data.get('producto') or data.get('producto_id')
    cantidad = data.get('cantidad', 1)
    
    response, status_code = inventario_service.reservar_stock(producto, cantidad)
    return jsonify(response), status_code


@inventario_bp.route('/compensacion', methods=['POST'])
def compensar_reserva() -> Tuple[dict, int]:
    """
    Endpoint para compensar (liberar) una reserva de stock.
    
    Request body:
        {
            "reserva_id": str
        }
    
    Returns:
        200: Compensación exitosa
    """
    data = request.get_json()
    reserva_id = data.get('reserva_id')
    
    response, status_code = inventario_service.compensar_reserva(reserva_id)
    return jsonify(response), status_code