#Utilidades compartidas entre microservicios 
# para manejo de transacciones y aplicar DRY
import random
import time
import uuid

# Simula latencia de red o procesamiento
def simular_latencia(min_sec=0.1, max_sec=1):
    time.sleep(random.uniform(min_sec, max_sec))


def tiene_exito(probabilidad=0.5):
#Simula exito/fallo aleatorio basado en probabilidad. 
# Devuelve true o false 
    return random.random() < probabilidad


def generar_id():
# COn la libreria uuid genera un id unico
    return str(uuid.uuid4())
