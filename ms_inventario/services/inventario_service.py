import logging
from typing import Dict, Optional, Tuple
import sys
import os
import threading

# Importar helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.transaction_helper import simular_latencia, generar_id

# Importar configuración
from ..config import (
    ESTADO_RESERVADO,
    ESTADO_CANCELADA,
    MSG_RESERVA_EXITOSA,
    MSG_PRODUCTO_NO_ENCONTRADO,
    MSG_STOCK_INSUFICIENTE,
    MSG_RESERVA_COMPENSADA,
    MSG_NO_RESERVA_COMPENSAR,
    INVENTARIO_INICIAL
)

logger = logging.getLogger(__name__)


class InventarioService:
    """Servicio de negocio para gestión de inventario y reservas"""
    
    def __init__(self):
        # Crear copia del inventario inicial
        self.inventario: Dict[str, Dict] = {k: v.copy() for k, v in INVENTARIO_INICIAL.items()}
        self.reservas_db: Dict[str, Dict] = {}
        self._lock = threading.Lock()  # Lock para operaciones concurrentes (CRÍTICO para stock)
    
    def obtener_inventario(self) -> Tuple[Dict, int]:
        """
        Obtiene el estado actual del inventario.
        
        Returns:
            Tupla con (inventario_dict, codigo_http)
        """
        logger.info("📦 Inventario solicitado")
        return self.inventario, 200
    
    def reservar_stock(self, producto: str, cantidad: int = 1) -> Tuple[Dict, int]:
        """
        Reserva stock de un producto.
        
        Args:
            producto: Nombre del producto (se convertirá a mayúsculas y se extraerá la primera palabra)
            cantidad: Cantidad a reservar (default: 1)
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        # Extraer primera palabra y convertir a mayúsculas
        # "Laptop Gamer" -> "LAPTOP", "Monitor 27 pulgadas" -> "MONITOR"
        producto_key = producto.split()[0].upper()
        logger.info(f"📦 Intentando reservar {cantidad}x {producto} (key: {producto_key})")
        
        # Simular latencia
        simular_latencia()
        
        # Verificar si el producto existe
        if producto_key not in self.inventario:
            logger.warning(f"❌ Producto {producto_key} no encontrado")
            return {
                "success": False,
                "error": MSG_PRODUCTO_NO_ENCONTRADO
            }, 409
        
        # Verificar si hay stock suficiente
        stock_disponible = self.inventario[producto_key]['stock']
        
        if stock_disponible < cantidad:
            logger.warning(f"❌ Stock insuficiente para {producto_key}. Disponible: {stock_disponible}, Requerido: {cantidad}")
            return {
                "success": False,
                "error": f"{MSG_STOCK_INSUFICIENTE}. Disponible: {stock_disponible}"
            }, 409
        
        # ÉXITO - Reservar stock
        with self._lock:
            reserva_id = generar_id()
            
            # Actualizar inventario
            self.inventario[producto_key]['stock'] -= cantidad
            self.inventario[producto_key]['reservado'] += cantidad
            
            # Guardar reserva
            self.reservas_db[reserva_id] = {
                "reserva_id": reserva_id,
                "producto": producto_key,
                "cantidad": cantidad,
                "estado": ESTADO_RESERVADO
            }
        
        logger.info(f"✅ Stock reservado: {self.reservas_db[reserva_id]}")
        logger.info(f"📊 Inventario actualizado - {producto_key}: stock={self.inventario[producto_key]['stock']}, reservado={self.inventario[producto_key]['reservado']}")
        
        return {
            "success": True,
            "reserva_id": reserva_id,
            "mensaje": MSG_RESERVA_EXITOSA
        }, 200
    
    def compensar_reserva(self, reserva_id: Optional[str]) -> Tuple[Dict, int]:
        """
        Compensa (libera) una reserva de stock.
        
        Args:
            reserva_id: ID de la reserva a compensar (opcional)
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        if not reserva_id:
            logger.warning("⚠️  Compensación llamada sin reserva_id")
            return {
                "success": True,
                "mensaje": MSG_NO_RESERVA_COMPENSAR
            }, 200
        
        # Buscar y liberar la reserva
        with self._lock:
            if reserva_id in self.reservas_db:
                reserva = self.reservas_db[reserva_id]
                producto = reserva['producto']
                cantidad = reserva['cantidad']
                
                # Actualizar inventario (devolver stock)
                self.inventario[producto]['stock'] += cantidad
                self.inventario[producto]['reservado'] -= cantidad
                
                # Marcar reserva como cancelada
                reserva['estado'] = ESTADO_CANCELADA
                
                logger.info(f"↩️  Reserva {reserva_id} cancelada exitosamente")
                logger.info(f"📊 Inventario actualizado - {producto}: stock={self.inventario[producto]['stock']}, reservado={self.inventario[producto]['reservado']}")
            else:
                logger.warning(f"⚠️  Reserva {reserva_id} no encontrada (quizás ya fue cancelada)")
        
        return {
            "success": True,
            "mensaje": MSG_RESERVA_COMPENSADA
        }, 200