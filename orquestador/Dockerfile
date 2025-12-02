FROM python:3.13.7-slim

WORKDIR /app

# Copiar common desde la raíz
COPY common/ ./common/

# Copiar el orquestador con su requirements.txt
COPY orquestador/ ./orquestador/

# Instalar dependencias desde el requirements.txt del orquestador
RUN pip install --no-cache-dir -r orquestador/requirements.txt

EXPOSE 5000

# Usar Granian como servidor WSGI con 2 workers para el orquestador
CMD ["granian", "--interface", "wsgi", "--host", "0.0.0.0", "--port", "5000", "--workers", "2", "orquestador.app:app"]