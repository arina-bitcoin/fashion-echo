# Этап сборки - устанавливаем зависимости
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Устанавливаем только необходимые для сборки пакеты
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей из правильного места (Backend/requirements.txt)
COPY Backend/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Финальный этап - создаем минимальный образ для запуска
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Устанавливаем только runtime зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Копируем установленные пакеты из этапа сборки
COPY --from=builder /root/.local /usr/local

# Копируем код приложения
COPY . .

# Создаем непривилегированного пользователя
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Создаем необходимые директории
RUN mkdir -p /app/media /app/logs /app/db /app/File_storage

# Устанавливаем права доступа
RUN chown -R appuser:appuser /app

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Переключаемся на непривилегированного пользователя
USER appuser

# Используем JSON формат для CMD
CMD ["uvicorn", "simple_app:app", "--host", "0.0.0.0", "--port", "8000"]