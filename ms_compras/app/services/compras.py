import logging
from typing import Dict, Optional, Tuple
import sys
import os
import threading

# Agregar el directorio padre al path para importar common
# Necesitamos ir 3 niveles arriba: services/ -> ms_compras/ -> microservices/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from common.transaction_helper import simular_latencia, tiene_exito, generar_id

#configuraciones del microservicio
from ..config import (
    ESTADO_CONFIRMADA,
    ESTADO_CANCELADA,
    MSG_COMPRA_EXITOSA,
    MSG_COMPRA_FALLIDA,
    MSG_COMPRA_CANCELADA,
    MSG_NO_COMPRA_COMPENSAR,
    PROBABILIDAD_EXITO
)


logger = logging.getLogger(__name__)


class ComprasService:

    def __init__(self):
        self.compras_db: Dict[str, Dict] = {}
        self._lock = threading.Lock()  # Lock para operaciones concurrentes
    
    def crear_compra(self, usuario_id: str, producto: str) -> Tuple[Dict, int]:
        """
        Crea una nueva compra.
    
        Args:
            usuario_id: ID del usuario que realiza la compra
            producto: Nombre del producto a comprar
        
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        logger.info(f'Registrando compra para usuario_id: {usuario_id} con producto: {producto}')

        simular_latencia()

        if not tiene_exito(0.5):
            logger.warning(f'Fallo al registrar compra para usuario_id: {usuario_id}')
            return {
                "success": False,
                "error": MSG_COMPRA_FALLIDA
            }, 409
        
        with self._lock:
            compra_id = generar_id()
            self.compras_db[compra_id] = {
                "compra_id": compra_id,
                "usuario_id": usuario_id,
                "producto": producto,
                "estado": ESTADO_CONFIRMADA
            }

        logger.info(f'Compra registrada exitosamente: {self.compras_db[compra_id]}')
        return {
            "success": True,
            "compra_id": compra_id,
            "mensaje": MSG_COMPRA_EXITOSA
        }, 200

    def listar_compras(self) -> Tuple[Dict, int]:
        """
        Lista todas las compras registradas.
    
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
    # Filtrar solo compras confirmadas
        compras_activas = [
            compra for compra in self.compras_db.values() 
            if compra["estado"] == ESTADO_CONFIRMADA
        ]
    
        logger.info(f'📋 Listado de compras solicitadas - Total activas: {len(compras_activas)} / Total general: {len(self.compras_db)}')
    
        return {
            "compras": compras_activas,
            "total_activas": len(compras_activas),
            "total_general": len(self.compras_db)
        }, 200
    
    def compensar_compra(self, compra_id: Optional[str]) -> Tuple[Dict, int]:
        """
        Compensa (cancela) una compra previamente registrada.
    
        Args:
            compra_id: ID de la compra a compensar (opcional)
        
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """

        logger.info(f'Iniciando compensación para compra_id: {compra_id}')

        #verificar si se proporcionó compra_id
        if not compra_id:
            logger.warning("Compensación llamada sin compra_id")
            return {
                "success": True,
                "mensaje": MSG_NO_COMPRA_COMPENSAR
            }, 200
        # Buscar y cancelar la compra

        with self._lock:
            if compra_id in self.compras_db:
                self.compras_db[compra_id]["estado"] = ESTADO_CANCELADA
                logger.info(f"Compra {compra_id} cancelada exitosamente")
            else:
                logger.warning(f"Compra {compra_id} no encontrada (quizás ya fue cancelada)")
        
        return {
            "success": True,
            "mensaje": MSG_COMPRA_CANCELADA
        }, 200