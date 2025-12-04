"""
Lógica de negocio para el servicio de catálogo
"""
import logging
import random
from typing import Dict, List, Tuple

from config import PRODUCTOS

logger = logging.getLogger(__name__)


class CatalogoService:
#Servicio de negocio para gestión del catálogo de productos
    
    def __init__(self):
        self.productos: List[Dict] = PRODUCTOS
    
    def obtener_producto_aleatorio(self) -> Tuple[Dict, int]:
#Obtiene un producto aleatorio del catálogo.

        producto = random.choice(self.productos)
        logger.info(f'🎲 Producto aleatorio seleccionado: {producto["nombre"]} (${producto["precio"]})')
        
        return producto, 200
    
    def obtener_catalogo_completo(self) -> Tuple[Dict, int]:

#Obtiene el catálogo completo de productos.

        logger.info(f'📚 Catálogo completo solicitado - Total de productos: {len(self.productos)}')
        
        return {
            "productos": self.productos,
            "total": len(self.productos)
        }, 200
    
    def buscar_producto_por_id(self, producto_id: str) -> Tuple[Dict, int]:
        """
        Busca un producto específico por su ID.
        
        Args:
            producto_id: ID del producto a buscar
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        for producto in self.productos:
            if producto["id"] == producto_id:
                logger.info(f'🔍 Producto encontrado: {producto["nombre"]}')
                return producto, 200
        
        logger.warning(f'❌ Producto {producto_id} no encontrado')
        return {"error": "Producto no encontrado"}, 404
