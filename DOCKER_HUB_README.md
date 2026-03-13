# Fashion Echo - Docker Image

Fashion Echo — это веб-приложение для покупки, продажи и обмена использованной одежды с фокусом на экологичность и социальную направленность.

## 🚀 Быстрый запуск

### Простой запуск
```bash
docker run -d -p 8000:8000 r2makhmetshin/fashion-eco-back:latest
```

### Запуск с переменными окружения
```bash
docker run -d \
  -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e DEBUG=false \
  -v $(pwd)/data:/app/db \
  r2makhmetshin/fashion-eco-back:latest
```

## 🏷️ Доступные теги

- `latest` - Последняя стабильная версия
- `v1.0.0` - Версия 1.0.0
- `dev` - Версия для разработки

## 🔧 Разработка с bind mount

Для разработки с автоматической перезагрузкой при изменении кода:

```bash
docker run -d \
  --name fashion-eco-dev \
  -p 8000:8000 \
  -v $(pwd):/app \
  -e ENVIRONMENT=development \
  -e DEBUG=true \
  r2makhmetshin/fashion-eco-back:latest \
  uvicorn Backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Команды для разработки

```bash
# Запуск в режиме разработки
docker run -it --rm \
  -p 8000:8000 \
  -v $(pwd):/app \
  -e ENVIRONMENT=development \
  r2makhmetshin/fashion-eco-back:latest \
  uvicorn Backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Подключение к контейнеру для отладки
docker exec -it fashion-eco-dev bash

# Просмотр логов
docker logs -f fashion-eco-dev
```

## 🌐 Endpoints

После запуска контейнера доступны следующие endpoints:

- **API**: `http://localhost:8000`
- **Документация**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **Redoc**: `http://localhost:8000/redoc`

## 🔧 Переменные окружения

| Переменная | Описание | Значение по умолчанию |
|------------|----------|----------------------|
| `SECRET_KEY` | Секретный ключ для JWT | `your-secret-key` |
| `DEBUG` | Режим отладки | `false` |
| `ENVIRONMENT` | Окружение (development/production) | `production` |
| `DATABASE_URL` | URL базы данных | `sqlite:///./db/fashion_eco.db` |
| `CORS_ORIGINS` | Разрешенные CORS origins | `http://localhost:3000` |

## 📦 Volumes

Рекомендуемые точки монтирования:

```bash
docker run -d \
  -p 8000:8000 \
  -v fashion_eco_db:/app/db \
  -v fashion_eco_media:/app/media \
  -v fashion_eco_storage:/app/File_storage \
  -v fashion_eco_logs:/app/logs \
  r2makhmetshin/fashion-eco-back:latest
```

## 🏥 Health Check

Образ включает встроенный health check, который проверяет:
- Доступность приложения на порту 8000
- Подключение к базе данных
- Общее состояние сервиса

```bash
# Проверка состояния
curl http://localhost:8000/health
```

Ответ health check:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-05T10:30:00.000000",
  "service": "Fashion Echo API",
  "version": "1.0.0",
  "database": "connected"
}
```

## 🐳 Docker Compose

Для полного стека с frontend используйте docker-compose:

```yaml
version: "3.9"
services:
  backend:
    image: r2makhmetshin/fashion-eco-back:latest
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key
    volumes:
      - ./db:/app/db
      - ./media:/app/media

  frontend:
    image: nginx:alpine
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
    depends_on:
      - backend
```

## 🔒 Безопасность

- Контейнер запускается от непривилегированного пользователя `appuser`
- Минимальный базовый образ `python:3.11-slim`
- Многоэтапная сборка для уменьшения размера образа
- Регулярные обновления безопасности

## 📊 Характеристики образа

- **Базовый образ**: `python:3.11-slim`
- **Размер**: < 500MB
- **Архитектуры**: `linux/amd64`
- **Python версия**: 3.11
- **Веб-сервер**: Uvicorn
- **База данных**: SQLite (встроенная)

## 🐛 Отладка

### Просмотр логов
```bash
docker logs your-container-name
```

### Подключение к контейнеру
```bash
docker exec -it your-container-name bash
```

### Проверка переменных окружения
```bash
docker exec your-container-name env
```

## 📚 Дополнительная информация

- **GitHub**: https://github.com/your-username/fashion-eco
- **Документация**: https://your-docs-url.com
- **Issues**: https://github.com/your-username/fashion-eco/issues

## 🤝 Поддержка

Если у вас возникли проблемы с использованием образа:

1. Проверьте логи: `docker logs container-name`
2. Убедитесь в корректности переменных окружения
3. Проверьте health check: `curl http://localhost:8000/health`
4. Создайте issue в GitHub репозитории

## 📄 Лицензия

MIT License - см. LICENSE файл в репозитории.