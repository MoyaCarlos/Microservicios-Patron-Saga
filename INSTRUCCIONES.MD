# Instrucciones de Uso - Patrón Saga con Docker y Traefik

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Red Docker externa `mired` creada (es la que se crea con docker network create)

---

## 🌐 Paso 1: Iniciar Traefik (Reverse Proxy)

Traefik debe estar corriendo **antes** de iniciar los microservicios.

```bash
cd traefik
docker compose up -d
```

**Verificar que Traefik está corriendo:**
```bash
docker ps | grep traefik
```

> **Importante:** Traefik gestiona todo el enrutamiento HTTP hacia los microservicios.

---