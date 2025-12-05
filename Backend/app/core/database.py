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
    """Генератор сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
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