"""
Servicio de orquestación usando patrón Saga
"""
import logging
import requests
import time
from typing import Dict, Tuple, List, Optional

from .config import (
    MS_CATALOGO_URL,
    MS_COMPRAS_URL,
    MS_PAGOS_URL,
    MS_INVENTARIO_URL,
    MSG_SAGA_EXITOSA,
    MSG_SAGA_FALLIDA,
    DELAY_ENTRE_PASOS,
    MAX_RETRIES,
    RETRY_BASE_DELAY
)

logger = logging.getLogger(__name__)


class SagaOrchestrator:
    """Orquestador del patrón Saga para coordinar microservicios"""
    
    def __init__(self):
        # Almacena los IDs de transacciones exitosas para compensar si falla algo
        self.transacciones_exitosas: Dict[str, str] = {}
    
    def _ejecutar_con_retry(self, operacion_nombre: str, operacion_func, *args) -> Tuple[bool, Optional[Dict], int]:
        """
        Ejecuta una operación con reintentos exponenciales.
        
        Args:
            operacion_nombre: Nombre de la operación para logging
            operacion_func: Función a ejecutar
            *args: Argumentos para la función
            
        Returns:
            Tupla (success, response, intentos_realizados)
        """
        for intento in range(1, MAX_RETRIES + 1):
            logger.info(f"🔄 [{operacion_nombre}] Intento {intento}/{MAX_RETRIES}")
            
            resultado = operacion_func(*args)
            
            if resultado:
                if intento > 1:
                    logger.info(f"✅ [{operacion_nombre}] Operación exitosa después de {intento} intentos")
                return True, resultado, intento
            else:
                logger.warning(f"❌ [{operacion_nombre}] Intento {intento} falló")
                
                if intento < MAX_RETRIES:
                    # Backoff exponencial: 1s, 2s, 4s
                    tiempo_espera = RETRY_BASE_DELAY * (2 ** (intento - 1))
                    logger.info(f"⏳ [{operacion_nombre}] Esperando {tiempo_espera}s antes del siguiente intento...")
                    time.sleep(tiempo_espera)
        
        logger.error(f"🚫 [{operacion_nombre}] Operación falló después de {MAX_RETRIES} intentos")
        return False, None, MAX_RETRIES
    
    def ejecutar_saga(self, usuario_id: str, producto_nombre: str, monto: float) -> Tuple[Dict, int]:
        """
        Ejecuta la saga completa: Catalogo → Compras → Pagos → Inventario
        
        Flujo:
        1. Obtener información del producto del catálogo
        2. Crear compra
        3. Procesar pago
        4. Reservar inventario
        
        Si algún paso falla (409), ejecuta compensaciones en orden inverso
        
        Args:
            usuario_id: ID del usuario que realiza la compra
            producto_nombre: Nombre del producto a comprar
            monto: Monto a pagar
            
        Returns:
            Tupla con (respuesta_dict, codigo_http)
        """
        logger.info(f"🎬 Iniciando Saga para usuario {usuario_id} - Producto: {producto_nombre}")
        self.transacciones_exitosas = {}  # Reset
        
        try:
            # PASO 1: Validar que el producto existe en el catálogo
            logger.info("⏳ Paso 1/4: Validando producto en catálogo...")
            producto_info = self._validar_producto_en_catalogo(producto_nombre)
            
            if not producto_info:
                logger.error(f"❌ Producto '{producto_nombre}' no existe en catálogo - Saga cancelada")
                return {
                    "success": False,
                    "error": f"Producto '{producto_nombre}' no existe en el catálogo"
                }, 404
            
            logger.info(f"✅ Paso 1/4: Producto validado - {producto_info['nombre']} (${producto_info['precio']})")
            time.sleep(DELAY_ENTRE_PASOS)
            
            # PASO 2: Crear compra con RETRY
            logger.info("⏳ Paso 2/4: Creando compra...")
            success, compra_result, intentos = self._ejecutar_con_retry(
                "Crear Compra",
                self._llamar_compras,
                usuario_id,
                producto_nombre
            )
            
            if not success:
                logger.error(f"❌ Paso 2/4: Fallo al crear compra después de {intentos} intentos")
                # No hay compensación (catálogo es read-only)
                return {
                    "success": False,
                    "error": f"Fallo al crear compra después de {intentos} intentos",
                    "intentos_realizados": intentos
                }, 409
            
            self.transacciones_exitosas['compra_id'] = compra_result['compra_id']
            logger.info(f"✅ Paso 2/4: Compra creada - ID: {compra_result['compra_id']} (intentos: {intentos})")
            time.sleep(DELAY_ENTRE_PASOS)
            
            # PASO 3: Procesar pago con RETRY
            logger.info("⏳ Paso 3/4: Procesando pago...")
            success, pago_result, intentos = self._ejecutar_con_retry(
                "Procesar Pago",
                self._llamar_pagos,
                usuario_id,
                monto,
                compra_result['compra_id']
            )
            
            if not success:
                logger.error(f"❌ Paso 3/4: Fallo al procesar pago después de {intentos} intentos")
                # FALLO: Compensar compra
                self._ejecutar_compensaciones(['compras'])
                return {
                    "success": False,
                    "error": f"Fallo al procesar pago después de {intentos} intentos - {MSG_SAGA_FALLIDA}",
                    "intentos_realizados": intentos
                }, 409
            
            self.transacciones_exitosas['pago_id'] = pago_result['pago_id']
            logger.info(f"✅ Paso 3/4: Pago procesado - ID: {pago_result['pago_id']} (intentos: {intentos})")
            time.sleep(DELAY_ENTRE_PASOS)
            
            # PASO 4: Reservar inventario (SIN RETRY - error permanente si falla por stock)
            logger.info("⏳ Paso 4/4: Reservando inventario...")
            reserva_result = self._llamar_inventario(producto_nombre)
            if not reserva_result:
                logger.error("❌ Paso 4/4: Fallo al reservar inventario (stock insuficiente o producto no encontrado)")
                # FALLO: Compensar pagos y compras (orden inverso)
                self._ejecutar_compensaciones(['pagos', 'compras'])
                return {
                    "success": False,
                    "error": "Fallo al reservar inventario - " + MSG_SAGA_FALLIDA
                }, 409
            
            self.transacciones_exitosas['reserva_id'] = reserva_result['reserva_id']
            logger.info(f"✅ Paso 4/4: Inventario reservado - ID: {reserva_result['reserva_id']}")
            
            # ✅ SAGA EXITOSA
            logger.info("🎉 Saga completada exitosamente")
            return {
                "success": True,
                "mensaje": MSG_SAGA_EXITOSA,
                "datos": {
                    "producto": producto_info,
                    "compra_id": compra_result['compra_id'],
                    "pago_id": pago_result['pago_id'],
                    "reserva_id": reserva_result['reserva_id']
                }
            }, 200
            
        except Exception as e:
            logger.error(f"❌ Error inesperado en Saga: {e}")
            self._ejecutar_compensaciones(['pagos', 'compras'])
            return {"success": False, "error": "Error interno del servidor"}, 500
    
    def _llamar_catalogo(self) -> Optional[Dict]:
        """Llama al microservicio de catálogo para obtener un producto"""
        try:
            response = requests.get(f"{MS_CATALOGO_URL}/producto", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a catálogo: {e}")
        return None
    
    def _validar_producto_en_catalogo(self, nombre_producto: str) -> Optional[Dict]:
        """
        Valida que un producto existe en el catálogo por nombre.
        
        Args:
            nombre_producto: Nombre del producto a validar
            
        Returns:
            Diccionario con información del producto si existe, None si no
        """
        try:
            response = requests.get(f"{MS_CATALOGO_URL}/buscar/{nombre_producto}", timeout=5)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Producto '{nombre_producto}' no encontrado en catálogo")
                return None
        except Exception as e:
            logger.error(f"Error validando producto en catálogo: {e}")
        return None
    
    def _llamar_compras(self, usuario_id: str, producto: str) -> Optional[Dict]:
        """Crea una compra"""
        try:
            response = requests.post(
                f"{MS_COMPRAS_URL}/transaccion",
                json={"usuario_id": usuario_id, "producto": producto},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a compras: {e}")
        return None
    
    def _llamar_pagos(self, usuario_id: str, monto: float, compra_id: str) -> Optional[Dict]:
        """Procesa un pago"""
        try:
            response = requests.post(
                f"{MS_PAGOS_URL}/transaccion",
                json={"usuario_id": usuario_id, "monto": monto, "compra_id": compra_id},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a pagos: {e}")
        return None
    
    def _llamar_inventario(self, producto: str) -> Optional[Dict]:
        """Reserva inventario"""
        try:
            response = requests.post(
                f"{MS_INVENTARIO_URL}/transaccion",
                json={"producto": producto, "cantidad": 1},
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"Error llamando a inventario: {e}")
        return None
    
    def _ejecutar_compensaciones(self, servicios: List[str]):
        """
        Ejecuta compensaciones en orden inverso
        
        Args:
            servicios: Lista de servicios a compensar en orden ['pagos', 'compras']
        """
        logger.warning(f"⚠️  Ejecutando compensaciones para: {servicios}")
        time.sleep(DELAY_ENTRE_PASOS)
        
        for servicio in servicios:
            if servicio == 'pagos' and 'pago_id' in self.transacciones_exitosas:
                logger.info(f"↩️  Compensando pago {self.transacciones_exitosas['pago_id']}...")
                self._compensar_pago(self.transacciones_exitosas['pago_id'])
                time.sleep(DELAY_ENTRE_PASOS)
            
            elif servicio == 'compras' and 'compra_id' in self.transacciones_exitosas:
                logger.info(f"↩️  Compensando compra {self.transacciones_exitosas['compra_id']}...")
                self._compensar_compra(self.transacciones_exitosas['compra_id'])
                time.sleep(DELAY_ENTRE_PASOS)
    
    def _compensar_pago(self, pago_id: str):
        """Compensa (reembolsa) un pago"""
        try:
            response = requests.post(
                f"{MS_PAGOS_URL}/compensacion",
                json={"pago_id": pago_id},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"✅ Pago {pago_id} compensado exitosamente")
        except Exception as e:
            logger.error(f"Error compensando pago: {e}")
    
    def _compensar_compra(self, compra_id: str):
        """Compensa (cancela) una compra"""
        try:
            response = requests.post(
                f"{MS_COMPRAS_URL}/compensacion",
                json={"compra_id": compra_id},
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"✅ Compra {compra_id} compensada exitosamente")
        except Exception as e:
            logger.error(f"Error compensando compra: {e}")