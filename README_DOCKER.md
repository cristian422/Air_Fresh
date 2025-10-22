# 🐳 Guía de Docker para Air Fresh

Este proyecto está completamente dockerizado, incluyendo la base de datos PostgreSQL y el backend FastAPI.

## 📋 Prerequisitos

- Docker y Docker Compose instalados
- Puerto 8000 y 5432 disponibles (o modifica el `.env`)

## 🚀 Inicio Rápido

### 1. Configurar variables de entorno

```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita .env con tus credenciales si es necesario
```

### 2. Levantar los servicios

```bash
# Construir y levantar todos los servicios
docker-compose up --build

# O en modo detached (segundo plano)
docker-compose up -d --build
```

### 3. Verificar que todo funciona

- API Docs: http://localhost:8000/docs
- Base de datos: PostgreSQL en `localhost:5432`

## 🛠️ Comandos Útiles

### Ver logs
```bash
# Todos los servicios
docker-compose logs -f

# Solo backend
docker-compose logs -f backend

# Solo base de datos
docker-compose logs -f db
```

### Detener servicios
```bash
# Detener sin eliminar
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener, eliminar contenedores Y volúmenes (¡cuidado, elimina los datos!)
docker-compose down -v
```

### Reconstruir servicios
```bash
# Reconstruir backend después de cambios en código
docker-compose up --build backend

# Reconstruir todo
docker-compose up --build
```

### Acceder a la base de datos
```bash
# Conectar a PostgreSQL dentro del contenedor
docker-compose exec db psql -U postgres -d Airfresh

# O desde tu máquina local (si tienes psql instalado)
psql -h localhost -p 5432 -U postgres -d Airfresh
```

### Ejecutar comandos en el contenedor
```bash
# Bash en el backend
docker-compose exec backend bash

# Bash en la base de datos
docker-compose exec db bash
```

## 🔧 Configuración

### Variables de Entorno

Las siguientes variables se pueden configurar en el archivo `.env`:

```env
# Base de Datos
POSTGRES_USER=postgres
POSTGRES_PASSWORD=tallerdedi1
POSTGRES_DB=Airfresh

# Backend
PORT=8000
WORKERS=2
```

### Arquitectura

```
┌─────────────────┐
│   Backend       │
│   (FastAPI)     │
│   Port: 8000    │
└────────┬────────┘
         │
         │ DATABASE_URL
         │
┌────────▼────────┐
│   PostgreSQL    │
│   Port: 5432    │
│   Volume: db_data│
└─────────────────┘
```

### Volúmenes

- `db_data`: Persiste los datos de PostgreSQL entre reinicios

## 🐛 Troubleshooting

### El backend no puede conectar a la base de datos

```bash
# Verifica que el servicio db esté saludable
docker-compose ps

# Revisa los logs
docker-compose logs db
```

### Puerto ya en uso

Edita `.env` y cambia el puerto:
```env
PORT=8080
```

Luego en `docker-compose.yml` actualiza:
```yaml
ports:
  - "8080:8080"
```

### Limpiar todo y empezar de cero

```bash
# Detener y eliminar todo (contenedores, redes, volúmenes)
docker-compose down -v

# Eliminar imágenes antiguas
docker-compose rm -f

# Reconstruir desde cero
docker-compose up --build
```

## 📝 Desarrollo

### Hot Reload (Desarrollo)

Para desarrollo con recarga automática, usa `Dockerfile.dev`:

1. Crea un `docker-compose.dev.yml`:
```yaml
services:
  backend:
    build:
      dockerfile: Dockerfile.dev
    volumes:
      - ./Backend:/app/Backend
```

2. Ejecuta:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Ejecutar migraciones o scripts

```bash
# Ejecutar dentro del contenedor
docker-compose exec backend python -m Backend.script_name
```

## 🔒 Seguridad

⚠️ **IMPORTANTE**: 
- Cambia las contraseñas por defecto en producción
- No commitees el archivo `.env` al repositorio
- Usa secrets de Docker en producción

## 📚 Más Información

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
