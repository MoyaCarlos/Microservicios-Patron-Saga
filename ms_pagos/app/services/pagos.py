import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import sys
import os
import threading

# Agregar el directorio padre al path para importar common
#sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
#from common.transaction_helper import simular_latencia, tiene_exito, generar_id

from ..utils.transaction_helper import simular_latencia, tiene_exito, generar_id
from ..config import (
    ESTADO_APROBADO, 
    ESTADO_REEMBOLSADO,
    MSG_PAGO_EXITOSO,
    MSG_PAGO_FALLIDO,
    MSG_PAGO_REEMBOLSADO,
    MSG_NO_PAGO_COMPENSAR,
    PROBABILIDAD_EXITO
)

logger = logging.getLogger(__name__)


class PagoService:
    """Servicio de negocio para gestión de pagos"""
    
    def __init__(self):
        self.pagos_db: Dict[str, Dict] = {}
        self._lock = threading.Lock()  # Lock para operaciones concurrentes
    
    def procesar_pago(self, usuario_id: str, monto: float, compra_id: str) -> Tuple[Dict, int]:
        """
        Procesa un pago para una compra.
        
        Args:
            usuario_id: ID del usuario que realiza el pago
            monto: Monto a pagar
            compra_id: ID de la compra asociada
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        logger.info(f'💳 Procesando pago para usuario_id: {usuario_id} por monto: ${monto}')
        
        # Simular latencia de procesamiento
        simular_latencia()
        
        # Simular éxito o fallo aleatorio
        if not tiene_exito(0.5):
            logger.warning(f'❌ Fallo al procesar pago para usuario {usuario_id}')
            return {
                "success": False,
                "error": MSG_PAGO_FALLIDO
            }, 409
        
        # ÉXITO - Registrar pago
        with self._lock:
            pago_id = generar_id()
            self.pagos_db[pago_id] = {
                "pago_id": pago_id,
                "usuario_id": usuario_id,
                "monto": monto,
                "compra_id": compra_id,
                "estado": ESTADO_APROBADO,
                "fecha": datetime.now().isoformat()
            }
        
        logger.info(f'✅ Pago procesado exitosamente: {self.pagos_db[pago_id]}')
        
        return {
            "success": True,
            "pago_id": pago_id,
            "mensaje": MSG_PAGO_EXITOSO
        }, 200
    
    def compensar_pago(self, pago_id: Optional[str]) -> Tuple[Dict, int]:
        """
        Compensa (reembolsa) un pago previamente procesado.
        
        Args:
            pago_id: ID del pago a compensar
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        if not pago_id:
            logger.warning("⚠️  Compensación llamada sin pago_id")
            return {
                "success": True,
                "mensaje": MSG_NO_PAGO_COMPENSAR
            }, 200
        
        # Buscar y reembolsar el pago
        with self._lock:
            if pago_id in self.pagos_db:
                self.pagos_db[pago_id]['estado'] = ESTADO_REEMBOLSADO
                logger.info(f"↩️  Pago {pago_id} reembolsado exitosamente")
            else:
                logger.warning(f"⚠️  Pago {pago_id} no encontrado (quizás ya fue reembolsado)")
        
        return {
            "success": True,
            "mensaje": MSG_PAGO_REEMBOLSADO
        }, 200
    
    def listar_pagos(self) -> Tuple[Dict, int]:
        """
        Lista todos los pagos registrados.
        
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        logger.info(f'📋 Listado de pagos solicitados - Total: {len(self.pagos_db)}')
        
        return {
            "pagos": list(self.pagos_db.values()),
            "total": len(self.pagos_db)
        }, 200