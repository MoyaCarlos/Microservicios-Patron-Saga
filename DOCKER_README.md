# 🐳 Docker - Patrón SAGA con Traefik

## 📋 Resumen

Esta configuración implementa el **Patrón SAGA** orquestado con 5 servicios:
- **Traefik**: Reverse proxy y load balancer
- **Orquestador**: Coordina la saga y maneja compensaciones
- **ms-catalogo**: Gestión de productos
- **ms-compras**: Registro de compras
- **ms-pagos**: Procesamiento de pagos
- **ms-inventario**: Control de stock

## 🚀 Uso

### Levantar todos los servicios:
```bash
docker compose up --build
```

### Levantar en background:
```bash
docker compose up -d --build
```

### Ver logs:
```bash
docker compose logs -f
```

### Detener servicios:
```bash
docker compose down
```

### Limpiar todo (incluyendo volúmenes):
```bash
docker compose down -v
```

## 🌐 Endpoints (vía Traefik)

Una vez levantados los servicios, accede a:

- **Traefik Dashboard**: http://localhost:8080
- **Orquestador**: http://localhost/orquestador/compra (POST)
- **Catálogo**: http://localhost/ms_catalogo/health
- **Compras**: http://localhost/ms_compras/health
- **Pagos**: http://localhost/ms_pagos/health
- **Inventario**: http://localhost/ms_inventario/health

## 📡 Comunicación Interna

Los microservicios se comunican entre sí usando **nombres DNS de Docker**:
- `ms-catalogo:5001`
- `ms-compras:5002`
- `ms-pagos:5003`
- `ms-inventario:5004`

Traefik enruta el tráfico externo usando path prefixes.

## 🧪 Probar la SAGA

### Validación de Catálogo

El sistema **valida que el producto existe** en el catálogo **antes** de ejecutar la saga.

### Patrón Retry

Implementa **3 reintentos** con backoff exponencial (1s, 2s, 4s) para fallos transitorios.

### Ejemplo de Compra

```bash
curl -X POST http://localhost/orquestador/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "user123", "producto": "Laptop", "monto": 1500.00}'
```

**Parámetros requeridos:**
- `usuario_id`: Identificador del usuario
- `producto`: Nombre del producto (debe existir en catálogo)
- `monto`: Monto a pagar

**Probabilidad de éxito:** 50% por intento (87.5% con 3 reintentos)

## 🏗️ Arquitectura

```
Internet → Traefik (80) → Microservicios (red interna)
                ↓
        Dashboard (8080)
```

### Red Docker: `mired`
Todos los servicios están en la misma red bridge para comunicación interna.

## ⚙️ Configuración de Workers

- **Orquestador**: 4 workers (alta carga)
- **Microservicios**: 2 workers cada uno
- # para consistencia actualmente se usa 1 solo worker

## ⚙️ Variables de Entorno

El orquestador usa estas variables (definidas en docker-compose.yml):
- `MS_CATALOGO_URL=http://ms-catalogo:5001`
- `MS_COMPRAS_URL=http://ms-compras:5002`
- `MS_PAGOS_URL=http://ms-pagos:5003`
- `MS_INVENTARIO_URL=http://ms-inventario:5004`

## 🔄 Configuración de Resilencia

- **Patrón Retry**: Máximo 3 intentos con backoff exponencial
- **Probabilidad de éxito**: 50% por intento (configurable en `config.py`)
- **Validación temprana**: Verifica catálogo antes de iniciar transacciones

## 📦 Imágenes Base

Todos los servicios usan `python:3.13.7-slim` para optimizar tamaño.

## 🔍 Troubleshooting

### Ver estado de contenedores:
```bash
docker compose ps
```

### Inspeccionar logs de un servicio específico:
```bash
docker compose logs -f orquestador
docker compose logs -f ms-catalogo
```

### Reconstruir un servicio específico:
```bash
docker compose up -d --build orquestador
```

### Verificar red:
```bash
docker network inspect mired
```
