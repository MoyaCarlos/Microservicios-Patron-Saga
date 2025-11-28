# Catalogo Flask application
from flask import Flask, jsonify
import logging
import random
# La libreria logging es para logs de informacion, 
# se imprime en la terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("__name__")

app = Flask(__name__)

PRODUCTOS = [
    {"id": "prod_001", "nombre": "Laptop Gamer", "precio": 1500.00, "categoria": "Electrónica"},
    {"id": "prod_002", "nombre": "Mouse Inalámbrico", "precio": 25.99, "categoria": "Accesorios"},
    {"id": "prod_003", "nombre": "Teclado Mecánico", "precio": 89.99, "categoria": "Accesorios"},
    {"id": "prod_004", "nombre": "Monitor 27 pulgadas", "precio": 350.00, "categoria": "Electrónica"},
    {"id": "prod_005", "nombre": "Auriculares Bluetooth", "precio": 79.99, "categoria": "Audio"},
]

# metodo get para obtener un produto aleatorio. Codigo 200
@app.route("/producto", methods=["GET"])
def obtener_producto():
    producto = PRODUCTOS[random.randint(0, len(PRODUCTOS) - 1)]
    logger.info(f'Producto seleccionado: {producto}')
    return jsonify(producto), 200
# metodo get para obtener el catalogo completo. Codigo 200
@app.route("/catalogo_completo", methods=["GET"])
def obtener_catalogo():
    logger.info(f'Catálogo completo solicitado - Total de productos: {len(PRODUCTOS)}')
    return jsonify({"productos": PRODUCTOS, "total": len(PRODUCTOS)}), 200

# metodo de health check. Codigo 200 (lei que es una buena practica)
@app.route("/health", methods=["GET"])
def health():
    """Health check"""
    return jsonify({"status": "ok", "service": "ms-catalogo"}), 200


if __name__ == "__main__":
    logger.info("Iniciando ms-catalogo en puerto")
    app.run(host="0.0.0.0", port=5001, debug=True)