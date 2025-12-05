# endpoints del microservicio de pagos

from flask import Blueprint, jsonify, request
from typing import Tuple
from .services.compras_service import ComprasService
from .config import SERVICE_NAME

# Crear blueprint para las rutas
compras_bp = Blueprint('compras', __name__)

#instancia del servicio
compra_service = ComprasService()

@compras_bp.route("/health", methods=["GET"])
def health() -> Tuple[dict, int]:
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200

@compras_bp.route("/transaccion", methods=["POST"])
def crear_transaccion() -> Tuple[dict, int]:
    """
    Endpoint para crear una transacción de compra.
    
    Request body:
        {
            "usuario_id": str,
            "producto": str
        }
    
    Returns:
        200: Compra creada exitosamente
        409: Error al crear compra
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    producto = data.get("producto")
    response, status_code = compra_service.crear_compra(usuario_id, producto)
    return jsonify(response), status_code

@compras_bp.route("/compras", methods=["GET"])
def ver_compras() -> Tuple[dict, int]:
    """
    Endpoint para listar todas las compras.
    
    Returns:
        200: Lista de compras
    """
    response, status_code = compra_service.listar_compras()
    return jsonify(response), status_code

@compras_bp.route('/compensacion', methods=['POST'])
def compensar_transaccion() -> Tuple[dict, int]:
    """
    Endpoint para compensar (cancelar) una compra.
    
    Request body:
        {
            "compra_id": str
        }
    
    Returns:
        200: Compensación exitosa
    """
    data = request.get_json()
    compra_id = data.get('compra_id')
    
    response, status_code = compra_service.compensar_compra(compra_id)
    return jsonify(response), status_code