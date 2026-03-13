# Fashion Eco - Makefile для удобного управления

.PHONY: help build up down logs clean test lint format

# Переменные
COMPOSE_FILE = docker-compose.yml
COMPOSE_DEV_FILE = docker-compose.dev.yml

help: ## Показать справку
	@echo "Доступные команды:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Собрать все образы
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## Запустить приложение в production режиме
	docker-compose -f $(COMPOSE_FILE) up -d

up-dev: ## Запустить приложение в development режиме
	docker-compose -f $(COMPOSE_DEV_FILE) up -d

up-dev-tools: ## Запустить приложение в dev режиме с инструментами
	docker-compose -f $(COMPOSE_DEV_FILE) --profile dev-tools up -d

down: ## Остановить все сервисы
	docker-compose -f $(COMPOSE_FILE) down
	docker-compose -f $(COMPOSE_DEV_FILE) down

logs: ## Показать логи всех сервисов
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## Показать логи backend
	docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend: ## Показать логи frontend
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

ps: ## Показать статус контейнеров
	docker-compose -f $(COMPOSE_FILE) ps

restart: ## Перезапустить все сервисы
	make down
	make up

restart-dev: ## Перезапустить в dev режиме
	docker-compose -f $(COMPOSE_DEV_FILE) down
	make up-dev

clean: ## Очистить все контейнеры и volumes
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker-compose -f $(COMPOSE_DEV_FILE) down -v --remove-orphans
	docker system prune -f

clean-all: ## Полная очистка (включая образы)
	make clean
	docker system prune -af --volumes

backup-db: ## Создать резервную копию БД
	docker-compose -f $(COMPOSE_FILE) exec postgres pg_dump -U fashion_user fashion_eco > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## Восстановить БД из резервной копии (указать файл: make restore-db FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then echo "Укажите файл: make restore-db FILE=backup.sql"; exit 1; fi
	docker-compose -f $(COMPOSE_FILE) exec -T postgres psql -U fashion_user fashion_eco < $(FILE)

shell-backend: ## Подключиться к backend контейнеру
	docker-compose -f $(COMPOSE_FILE) exec backend bash

shell-db: ## Подключиться к PostgreSQL
	docker-compose -f $(COMPOSE_FILE) exec postgres psql -U fashion_user fashion_eco


test: ## Запустить тесты
	docker-compose -f $(COMPOSE_FILE) exec backend pytest -v

test-cov: ## Запустить тесты с покрытием
	docker-compose -f $(COMPOSE_FILE) exec backend pytest --cov=app --cov-report=html

lint: ## Проверить код линтерами
	docker-compose -f $(COMPOSE_FILE) exec backend flake8 app/
	docker-compose -f $(COMPOSE_FILE) exec backend mypy app/

format: ## Отформатировать код
	docker-compose -f $(COMPOSE_FILE) exec backend black app/
	docker-compose -f $(COMPOSE_FILE) exec backend isort app/

health: ## Проверить health checks всех сервисов
	@echo "Проверка health checks..."
	@curl -f http://localhost/health && echo "✅ Nginx Proxy OK" || echo "❌ Nginx Proxy FAIL"
	@curl -f http://localhost:3000/health && echo "✅ Frontend OK" || echo "❌ Frontend FAIL"
	@curl -f http://localhost:8000/health && echo "✅ Backend OK" || echo "❌ Backend FAIL"

stats: ## Показать статистику использования ресурсов
	docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

update: ## Обновить образы до последних версий
	docker-compose -f $(COMPOSE_FILE) pull
	make build
	make up

# Команды для CI/CD
ci-build: ## Сборка для CI
	docker-compose -f $(COMPOSE_FILE) build

ci-test: ## Тесты для CI
	docker-compose -f $(COMPOSE_FILE) up -d postgres redis
	sleep 10
	docker-compose -f $(COMPOSE_FILE) run --rm backend pytest
	docker-compose -f $(COMPOSE_FILE) down

# Команды для production
prod-deploy: ## Деплой в production
	@echo "Деплой в production..."
	make build
	docker-compose -f $(COMPOSE_FILE) --profile production up -d
	make health

prod-backup: ## Создать полный backup для production
	mkdir -p backups/$(shell date +%Y%m%d)
	make backup-db
	docker run --rm -v fashion_eco_app-media:/data -v $(PWD)/backups/$(shell date +%Y%m%d):/backup alpine tar czf /backup/media.tar.gz -C /data .
	docker run --rm -v fashion_eco_file-storage:/data -v $(PWD)/backups/$(shell date +%Y%m%d):/backup alpine tar czf /backup/files.tar.gz -C /data .