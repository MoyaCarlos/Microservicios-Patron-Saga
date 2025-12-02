FROM python:3.13.7-slim

WORKDIR /app

# Copiar common desde la raíz
COPY common/ ./common/

# Copiar el microservicio con su requirements.txt
COPY ms_inventario/ ./ms_inventario/

# Instalar dependencias desde el requirements.txt del microservicio
RUN pip install --no-cache-dir -r ms_inventario/requirements.txt

EXPOSE 5004

# Usar Granian como servidor WSGI con 1 worker (memoria compartida)
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "5004", "--workers", "1", "ms_inventario.app:app"]