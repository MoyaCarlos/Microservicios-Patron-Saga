"""
Definición de rutas/endpoints para el microservicio de pagos
"""
from flask import Blueprint, jsonify, request
from typing import Tuple
from .services.pago_service import PagoService
from .config import SERVICE_NAME

# Crear blueprint para las rutas
pagos_bp = Blueprint('pagos', __name__)

# Instancia única del servicio (Singleton pattern)
pago_service = PagoService()


@pagos_bp.route("/health", methods=["GET"])
def health() -> Tuple[dict, int]:
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@pagos_bp.route("/transaccion", methods=["POST"])
def procesar_pago() -> Tuple[dict, int]:
    """
    Endpoint para procesar un pago.
    
    Request body:
        {
            "usuario_id": str,
            "monto": float,
            "compra_id": str
        }
    
    Returns:
        200: Pago procesado exitosamente
        409: Error al procesar pago
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    monto = data.get('monto')
    compra_id = data.get('compra_id')
    
    response, status_code = pago_service.procesar_pago(usuario_id, monto, compra_id)
    return jsonify(response), status_code


@pagos_bp.route('/compensacion', methods=['POST'])
def compensar_pago() -> Tuple[dict, int]:
    """
    Endpoint para compensar (reembolsar) un pago.
    
    Request body:
        {
            "pago_id": str
        }
    
    Returns:
        200: Compensación exitosa
    """
    data = request.get_json()
    pago_id = data.get('pago_id')
    
    response, status_code = pago_service.compensar_pago(pago_id)
    return jsonify(response), status_code


@pagos_bp.route("/pagos", methods=["GET"])
def ver_pagos() -> Tuple[dict, int]:
    """
    Endpoint para listar todos los pagos.
    
    Returns:
        200: Lista de pagos
    """
    response, status_code = pago_service.listar_pagos()
    return jsonify(response), status_code
