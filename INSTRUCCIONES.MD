# Instrucciones de Uso - Patrón Saga con Docker y Traefik

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Red Docker externa `carlosred` creada (ver instrucciones abajo)

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

## 🔌 Paso 2: Crear la Red Docker (solo primera vez)

Los microservicios y Traefik se comunican a través de la red `carlosred`:

```bash
docker network create carlosred
```

> Si ya existe, verás un mensaje indicándolo. Puedes continuar sin problemas.

---

## 🚀 Paso 3: Construir e Iniciar los Microservicios

Desde la raíz del proyecto:

```bash
docker compose up -d --build
```

**Verificar que todos los servicios están corriendo:**
```bash
docker compose ps
```

Deberías ver 5 servicios:
- `ms-catalogo`
- `ms-compras`
- `ms-pagos`
- `ms-inventario`
- `orquestador`

---

## 🧪 Paso 4: Probar el Sistema

### Health Checks (verificar conectividad a través de Traefik)

```bash
# Orquestador
curl http://localhost/orquestador/health

# Catálogo
curl http://localhost/ms_catalogo/health

# Compras
curl http://localhost/ms_compras/health

# Pagos
curl http://localhost/ms_pagos/health

# Inventario
curl http://localhost/ms_inventario/health
```

**Respuesta esperada:**
```json
{"status": "ok", "service": "nombre-del-servicio"}
```

---

## 🛒 Paso 5: Realizar una Compra (Prueba del Patrón Saga)

### Validación de Catálogo

El sistema **valida que el producto existe** en el catálogo **antes** de ejecutar la saga.
Si el producto no existe, la transacción falla inmediatamente sin crear compensaciones.

### Patrón Retry Implementado

El orquestador implementa un **patrón de reintentos** para manejar fallos transitorios:
- **Máximo 3 intentos** por cada operación (compras y pagos)
- **Backoff exponencial**: 1s → 2s → 4s entre intentos
- Solo se aplica a fallos transitorios (no a errores permanentes como falta de stock)

### Ejemplo de Compra

```bash
curl -X POST http://localhost/orquestador/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "user123", "producto": "Laptop", "monto": 1500.00}'
```

**Parámetros requeridos:**
- `usuario_id`: Identificador del usuario
- `producto`: Nombre del producto a comprar (debe existir en catálogo)
- `monto`: Monto a pagar

**Casos posibles:**

#### ✅ Transacción Exitosa (50% probabilidad)
```json
{
  "success": true,
  "mensaje": "Saga completada exitosamente",
  "detalles": {
    "producto": "Laptop Gamer",
    "precio": 1200.0,
    "compra_id": "abc-123",
    "pago_id": "xyz-789",
    "reserva_id": "def-456"
  }
}
```

#### ❌ Producto No Encontrado (validación temprana)
```json
{
  "success": false,
  "error": "Producto 'iPhone' no encontrado en catálogo",
  "compensaciones": [],
  "paso_fallido": "catalogo"
}
```

#### ❌ Fallo con Compensación (después de reintentos)
```json
{
  "success": false,
  "error": "Fallo en el paso de pagos después de 3 intentos",
  "compensaciones": ["compras"],
  "mensaje": "La transacción ha sido revertida"
}
```

#### ❌ Fallo por Stock Insuficiente
```json
{
  "success": false,
  "error": "Stock insuficiente para LAPTOP",
  "compensaciones": ["pagos", "compras"],
  "paso_fallido": "inventario"
}
```

---

## 📊 Paso 6: Consultar Estado de los Servicios

### Ver Inventario Disponible
```bash
curl http://localhost/ms_inventario/inventario
```

**Respuesta:**
```json
{
  "LAPTOP": {"nombre": "Laptop Gamer", "precio": 1200.0, "stock": 5, "reservado": 0},
  "MOUSE": {"nombre": "Mouse Inalámbrico", "precio": 25.99, "stock": 10, "reservado": 0},
  "TECLADO": {"nombre": "Teclado Mecánico", "precio": 89.99, "stock": 3, "reservado": 0},
  "AURICULARES": {"nombre": "Auriculares Bluetooth", "precio": 59.99, "stock": 15, "reservado": 0},
  "MONITOR": {"nombre": "Monitor 27 pulgadas", "precio": 350.0, "stock": 8, "reservado": 0}
}
```

### Ver Compras Activas
```bash
curl http://localhost/ms_compras/compras
```

**Respuesta:**
```json
{
  "compras": [
    {
      "compra_id": "abc-123",
      "usuario_id": "user123",
      "producto": "Laptop Gamer",
      "estado": "confirmada"
    }
  ],
  "total_activas": 1,
  "total_general": 3
}
```

### Ver Pagos Registrados
```bash
curl http://localhost/ms_pagos/pagos
```

**Respuesta:**
```json
{
  "pagos": [
    {
      "pago_id": "xyz-789",
      "usuario_id": "user123",
      "monto": 1200.0,
      "compra_id": "abc-123",
      "estado": "aprobado",
      "fecha": "2025-11-26T10:30:45.123456"
    }
  ],
  "total": 1
}
```

---

## 🔄 Paso 7: Observar Compensaciones del Patrón Saga

Ejecuta varias compras para ver tanto transacciones exitosas como compensaciones:

```bash
# Ejecutar múltiples veces
curl -X POST http://localhost/orquestador/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "user456", "producto": "Mouse", "monto": 25.99}'
```

> **Nota:** El sistema tiene una **probabilidad del 50%** de éxito en compras y pagos para facilitar las pruebas.
> Con el patrón Retry (3 intentos), la probabilidad de éxito final es mayor (~87.5%).
> Ejecuta varias veces para observar:
> - ✅ Transacciones exitosas (con o sin reintentos)
> - ❌ Fallos con compensaciones automáticas
> - 🔄 Reintentos en los logs antes de éxito/fallo final

---

## 📊 Paso 8: Observar los Logs de Docker

Ver logs en tiempo real de todos los servicios:

```bash
docker compose logs -f
```

Ver logs de un servicio específico:

```bash
docker compose logs -f orquestador
docker compose logs -f ms-compras
docker compose logs -f ms-pagos
docker compose logs -f ms-inventario
```

**Ejemplo de logs exitosos (con reintentos):**
```
orquestador  | 🎬 Iniciando Saga para usuario user123
orquestador  | ⏳ Validando producto 'Laptop' en catálogo...
orquestador  | ✅ Producto encontrado: Laptop Gamer ($1200.0)
orquestador  | ⏳ Paso 1/4: Creando compra...
orquestador  | ⚠️  Intento 1/3 falló para compras. Esperando 1s antes de reintentar...
orquestador  | 🔄 Reintentando compras (intento 2/3)...
orquestador  | ✅ Paso 1/4: Compra creada - ID: abc-123
orquestador  | ⏳ Paso 2/4: Procesando pago...
orquestador  | ✅ Paso 2/4: Pago procesado - ID: xyz-789
orquestador  | ⏳ Paso 3/4: Reservando inventario...
orquestador  | ✅ Paso 3/4: Inventario reservado - ID: def-456
orquestador  | 🎉 Saga completada exitosamente
```

**Ejemplo de logs con compensación (después de agotar reintentos):**
```
orquestador  | 🎬 Iniciando Saga para usuario user123
orquestador  | ⏳ Validando producto 'Mouse' en catálogo...
orquestador  | ✅ Producto encontrado: Mouse Inalámbrico ($25.99)
orquestador  | ⏳ Paso 1/4: Creando compra...
orquestador  | ✅ Paso 1/4: Compra creada - ID: abc-123
orquestador  | ⏳ Paso 2/4: Procesando pago...
orquestador  | ⚠️  Intento 1/3 falló para pagos. Esperando 1s antes de reintentar...
orquestador  | 🔄 Reintentando pagos (intento 2/3)...
orquestador  | ⚠️  Intento 2/3 falló para pagos. Esperando 2s antes de reintentar...
orquestador  | 🔄 Reintentando pagos (intento 3/3)...
orquestador  | ❌ Paso 2/4: Fallo al procesar pago después de 3 intentos
orquestador  | ⚠️  Ejecutando compensaciones para: ['compras']
orquestador  | ↩️  Compensando compra abc-123...
orquestador  | ✅ Compra abc-123 compensada exitosamente
```

---

## 🛑 Paso 9: Detener los Servicios

### Detener microservicios (mantener Traefik corriendo)
```bash
docker compose down
```

### Detener todo incluyendo Traefik
```bash
docker compose down
cd traefik
docker compose down
```

### Limpiar recursos (imágenes, volúmenes, etc.)
```bash
docker compose down -v --rmi all
```

---

## 🏗️ Arquitectura del Sistema

### Versión Actual: 1.1.0

**Componentes:**
- **Traefik v3.1**: Reverse proxy y load balancer
- **Granian**: Servidor WSGI de alto rendimiento (Rust-based)
- **Flask 3.1.0**: Framework web para los microservicios
- **Docker Compose**: Orquestación de contenedores
- **Red Docker**: `carlosred` (bridge externa)

**Configuración de Workers:**
- **Orquestador**: 2 workers
- **Microservicios**: 1 worker cada uno

> **Nota sobre workers:** La versión actual usa 1 worker por microservicio para garantizar consistencia de datos con almacenamiento en memoria. Para entornos de producción con múltiples workers, se recomienda usar una base de datos compartida (PostgreSQL).

### Enrutamiento con Traefik

Traefik enruta las peticiones según el path:
- `http://localhost/orquestador/*` → Orquestador (puerto 5000)
- `http://localhost/ms_catalogo/*` → ms-catalogo (puerto 5001)
- `http://localhost/ms_compras/*` → ms-compras (puerto 5002)
- `http://localhost/ms_pagos/*` → ms-pagos (puerto 5003)
- `http://localhost/ms_inventario/*` → ms-inventario (puerto 5004)

---

## 🔍 Troubleshooting

### Los servicios no inician
```bash
# Verificar logs de errores
docker compose logs

# Verificar que Traefik está corriendo
docker ps | grep traefik

# Verificar que la red existe
docker network ls | grep carlosred
```

### Error "network carlosred not found"
```bash
docker network create carlosred
```

### Traefik no enruta correctamente
```bash
# Verificar logs de Traefik
cd traefik
docker compose logs -f

# Verificar que los servicios están en la red carlosred
docker network inspect carlosred
```

### Puerto 80 ocupado
Otro servicio está usando el puerto 80. Detén el servicio conflictivo o cambia el puerto de Traefik en `traefik/docker-compose.yml`.

### Rebuild completo (limpiar todo y empezar de nuevo)
```bash
# Detener todo
docker compose down -v --rmi all
cd traefik
docker compose down

# Reiniciar
cd ..
docker compose up -d --build
cd traefik
docker compose up -d
```

---

## 📝 Notas Adicionales

### Versionado de Imágenes

El proyecto usa versionado semántico para las imágenes Docker:
- `1.0.0`: Versión inicial con múltiples workers
- `1.0.1`: Ajuste de probabilidad de éxito a 95%
- `1.1.0`: **Versión actual** - 1 worker para consistencia

Para crear nuevas versiones, actualiza los tags en `docker-compose.yml` y reconstruye:
```bash
docker compose build
docker compose up -d
```

### Variables de Ambiente

Las URLs de los microservicios se configuran mediante variables de ambiente en `docker-compose.yml`:
- `MS_CATALOGO_URL=http://ms-catalogo:5001`
- `MS_COMPRAS_URL=http://ms-compras:5002`
- `MS_PAGOS_URL=http://ms-pagos:5003`
- `MS_INVENTARIO_URL=http://ms-inventario:5004`

Esto permite la comunicación entre contenedores usando DNS interno de Docker.

---

## 🎯 Resumen de Comandos Rápidos

```bash
# Inicio completo
docker network create carlosred
cd traefik && docker compose up -d && cd ..
docker compose up -d --build

# Prueba rápida
curl http://localhost/orquestador/health
curl -X POST http://localhost/orquestador/compra \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "test", "producto": "Laptop", "monto": 1500.00}'

# Ver logs
docker compose logs -f

# Detener todo
docker compose down
cd traefik && docker compose down
```
- Revisa los logs para identificar errores de importación
