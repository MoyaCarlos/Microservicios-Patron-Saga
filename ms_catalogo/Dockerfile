FROM python:3.13.7-slim

WORKDIR /app

# Copiar common desde la raíz
COPY common/ ./common/

# Copiar el microservicio con su requirements.txt
COPY ms_catalogo/ ./ms_catalogo/

# Instalar dependencias desde el requirements.txt del microservicio
RUN pip install --no-cache-dir -r ms_catalogo/requirements.txt

EXPOSE 5001

# Usar Granian como servidor WSGI con 1 worker
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "5001", "--workers", "1", "ms_catalogo.app:app"]
