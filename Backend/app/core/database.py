# import os
# from datetime import datetime
# from typing import Annotated

# from sqlalchemy import func, String, Text
# from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
# from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column
# from sqlalchemy.pool import StaticPool

# # from Backend.app.config import 
# from Backend.app.config import settings

# # Получаем URL для подключения
# DATABASE_URL = settings.DATABASE_URL

# # Создаем асинхронный движок для SQLite
# engine = create_async_engine(
#     DATABASE_URL,
#     # Важные настройки для SQLite
#     connect_args={"check_same_thread": False},  # Разрешаем доступ из разных потоков
#     poolclass=StaticPool,  # Статический пул для SQLite
#     echo=True  # Логирование SQL запросов (отключите в продакшене)
# )

# # Создаем фабрику сессий
# async_session_maker = async_sessionmaker(
#     engine, 
#     expire_on_commit=False,
#     autoflush=False
# )

# # Аннотации для часто используемых типов колонок
# int_pk = Annotated[int, mapped_column(primary_key=True)]
# created_at = Annotated[datetime, mapped_column(server_default=func.now())]
# updated_at = Annotated[datetime, mapped_column(
#     server_default=func.now(), 
#     onupdate=datetime.now
# )]
# str_uniq = Annotated[str, mapped_column(unique=True, nullable=False)]
# str_null_true = Annotated[str, mapped_column(nullable=True)]
# str_index = Annotated[str, mapped_column(index=True)]
# email_type = Annotated[str, mapped_column(String(255), index=True)]
# text_type = Annotated[str, mapped_column(Text)]

# class Base(AsyncAttrs, DeclarativeBase):
#     __abstract__ = True

#     @declared_attr.directive
#     def __tablename__(cls) -> str:
#         """Автоматическое имя таблицы на основе имени класса + 's'"""
#         return f"{cls.__name__.lower()}s"

#     # Автоматические timestamp поля для всех моделей
#     created_at: Mapped[created_at]
#     updated_at: Mapped[updated_at]

# async def create_db_and_tables():
#     """Создание всех таблиц в базе данных"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# async def drop_db_and_tables():
#     """Удаление всех таблиц (для тестов)"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.drop_all)









"""НАЧАЛО ФАЙЛА!!!"""
from Backend.app.config import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, declarative_base

# Получаем URL для подключения
DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронный движок для SQLite
engine = create_async_engine(
    DATABASE_URL,
    # Важные настройки для SQLite
    connect_args={"check_same_thread": False},  # Разрешаем доступ из разных потоков
    poolclass=StaticPool,  # Статический пул для SQLite
    echo=settings.DEBUG  # Логирование SQL запросов только в режиме отладки
)

"""Синхронная сессия -- не подходит"""
# # Берём URL из настроек и приводим его к sync-формату
# db_url = settings.DATABASE_URL
# if db_url.startswith("sqlite+aiosqlite"):
#     db_url = db_url.replace("sqlite+aiosqlite", "sqlite", 1)

# # Обычный синхронный engine
# engine = create_engine(
#     db_url,
#     connect_args={"check_same_thread": False},  # для SQLite
#     echo=True,  # можно выключить в проде
# )
""""""

# Базовый класс моделей
class Base(DeclarativeBase):
    pass

# Асинхронная сессия
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async_session_maker = AsyncSessionLocal

async def create_db_and_tables():
    """Создание всех таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

"""Синхронная сессия -- не подходит"""
# # Синхронная сессия
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Базовый класс моделей
# Base = declarative_base()


# def get_db():
#     """
#     Dependency для FastAPI — отдаёт sync-сессию.
#     """
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
""""""