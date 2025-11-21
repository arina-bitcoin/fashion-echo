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

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
# from .database import AsyncSessionLocal

""""""
from sqlalchemy.orm import DeclarativeBase, declared_attr

from Backend.app.config import settings

# Используем синхронный движок SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # Важно для SQLite
    echo=True  # Показывает SQL запросы в консоли (можно убрать)
)

# async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

""""""
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()
class Base(DeclarativeBase):
    pass
""""""

AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# class Base(AsyncAttrs, DeclarativeBase):
#     __abstract__ = True

#     @declared_attr.directive
#     def __tablename__(cls) -> str:
#         return f"{cls.__name__.lower()}s"

""""""
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
""""""

async def create_db_and_tables():
    """Создание всех таблиц в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)