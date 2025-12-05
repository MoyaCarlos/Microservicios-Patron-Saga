"""
Rutas del orquestador
"""
from flask import Blueprint, jsonify, request
from typing import Tuple
from .saga_service import SagaOrchestrator
from .config import SERVICE_NAME

orchestrator_bp = Blueprint('orchestrator', __name__)
saga_orchestrator = SagaOrchestrator()


@orchestrator_bp.route("/health", methods=["GET"])
def health() -> Tuple[dict, int]:
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@orchestrator_bp.route("/compra", methods=["POST"])
def procesar_compra() -> Tuple[dict, int]:
    """
    Endpoint principal que ejecuta la Saga completa.
    
    Request body:
        {
            "usuario_id": str,
            "producto": str,
            "monto": float
        }
    
    Returns:
        200: Saga completada exitosamente
        409: Fallo en algún paso, compensaciones ejecutadas
        500: Error interno
    """
    data = request.get_json()
    usuario_id = data.get('usuario_id')
    producto = data.get('producto')
    monto = data.get('monto')
    
    if not usuario_id:
        return jsonify({"success": False, "error": "usuario_id es requerido"}), 400
    
    if not producto:
        return jsonify({"success": False, "error": "producto es requerido"}), 400
    
    if not monto:
        return jsonify({"success": False, "error": "monto es requerido"}), 400
    
    response, status_code = saga_orchestrator.ejecutar_saga(usuario_id, producto, monto)
    return jsonify(response), status_code
