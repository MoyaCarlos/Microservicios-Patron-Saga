FROM python:3.13.7-slim

WORKDIR /app

COPY app/ ./app/
COPY requirements.txt .
COPY main.py .



# Copiar common desde la raíz
#COPY common/ ./common/

# Copiar el microservicio con su requirements.txt
#COPY ms_compras/ ./ms_compras/

# Instalar dependencias desde el requirements.txt del microservicio
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5002

# Usar Granian como servidor WSGI con 1 worker (memoria compartida)
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "5002", "--workers", "1", "main:app"]

