# Traefik
Primero hay que hacer docker compose up -d en la carpeta de traefik. Cambien el nombre de la red

# Docker

Luego de tener los microservicios en funcionamiento tenemos que hacer la imagen en docker y hacer que el trafico lo maneje traefik

Tambien necesitamos que cada microservicio tenga su propio Dockerfile y requirements.txt