# ====== Etapa 1: build de dependencias en ruedas ======
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY requirements.txt ./
RUN pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir --no-deps -r requirements.txt -w /wheels

# ====== Etapa 2: runtime minimal ======
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    WORKERS=2 \
    TZ=America/Bogota \
    APP_MODULE=Backend.main:app 

RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copia tu carpeta real
COPY Backend ./Backend
COPY Backend ./apScheduler

EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:${PORT}/docs || exit 1
CMD ["bash", "-lc", "uvicorn ${APP_MODULE} --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}"]
