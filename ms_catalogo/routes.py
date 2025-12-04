"""
Definición de rutas/endpoints para el microservicio de catálogo
"""
from flask import Blueprint, jsonify
from typing import Tuple
from services.catalogo_service import CatalogoService
from config import SERVICE_NAME

# Crear blueprint para las rutas
catalogo_bp = Blueprint('catalogo', __name__)

# Instancia única del servicio (Singleton pattern)
catalogo_service = CatalogoService()


@catalogo_bp.route("/health", methods=["GET"])
def health() -> Tuple[dict, int]:
    """Health check endpoint"""
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@catalogo_bp.route("/producto", methods=["GET"])
def obtener_producto_aleatorio() -> Tuple[dict, int]:
    """
    Endpoint para obtener un producto aleatorio del catálogo.
    
    Returns:
        200: Producto aleatorio
    """
    response, status_code = catalogo_service.obtener_producto_aleatorio()
    return jsonify(response), status_code


@catalogo_bp.route("/catalogo_completo", methods=["GET"])
def obtener_catalogo_completo() -> Tuple[dict, int]:
    """
    Endpoint para obtener el catálogo completo de productos.
    
    Returns:
        200: Lista completa de productos
    """
    response, status_code = catalogo_service.obtener_catalogo_completo()
    return jsonify(response), status_code


@catalogo_bp.route("/producto/<producto_id>", methods=["GET"])
def obtener_producto_por_id(producto_id: str) -> Tuple[dict, int]:
    """
    Endpoint para obtener un producto específico por ID.
    
    Args:
        producto_id: ID del producto
    
    Returns:
        200: Producto encontrado
        404: Producto no encontrado
    """
    response, status_code = catalogo_service.buscar_producto_por_id(producto_id)
    return jsonify(response), status_code
