# migrations/env.py
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Добавьте путь к проекту
from pathlib import Path

# Добавляем корень проекта в sys.path (как у тебя было)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
# Импортируйте Base и модели
from Backend.app.core.database import Base
from Backend.app.models.user import User
from Backend.app.models.ad import Ad

# Это конфигурация Alembic
config = context.config

# УПРОЩЕННАЯ настройка логирования - УБЕРИТЕ fileConfig
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# target_metadata для Alembic
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в офлайн-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()