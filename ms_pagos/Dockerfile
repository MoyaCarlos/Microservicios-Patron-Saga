FROM python:3.13.7-slim

WORKDIR /app

#copia de el modulo app
COPY app/ ./app/

#copia de el archivo requirements.txt
COPY requirements.txt .

#copia de el archivo main.py
COPY main.py .

# Copiar common desde la raíz
# El contendio de common lo copie en la carpeta utils. 
# COPY common/ ./common/


# Copiar el microservicio con su requirements.txt
#COPY ms_pagos/ ./ms_pagos/

# Instalar dependencias desde el requirements.txt del microservicio
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 5003



# Usar Granian como servidor WSGI con 1 worker (memoria compartida)
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "5003", "--workers", "1", "main:app"] 

