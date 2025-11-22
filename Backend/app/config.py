# import os
# from pydantic_settings import BaseSettings, SettingsConfigDict

# class Settings(BaseSettings):
#     # SQLite настройки
#     DB_NAME: str = "fashion_echo.db"
#     DB_PATH: str = "db"
    
#     # JWT настройки
#     SECRET_KEY: str = "your-secret-key-here"  # В продакшене используйте .env
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
#     REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
#     # Настройки приложения
#     DEBUG: bool = True
    
#     model_config = SettingsConfigDict(
#         env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env"),
#         env_file_encoding='utf-8'
#     )

# settings = Settings()

# def get_db_url():
#     """Генерация URL для подключения к SQLite"""
#     db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
#                           settings.DB_PATH, settings.DB_NAME)
#     return f"sqlite+aiosqlite:///{db_path}"

# def get_sync_db_url():
#     """URL для синхронных операций (Alembic миграции)"""
#     db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
#                           settings.DB_PATH, settings.DB_NAME)
#     return f"sqlite:///{db_path}"

from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "db" / "fashion_eco.db"

class Settings(BaseSettings):
    # Настройки БД
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_PATH}"
    
    # JWT настройки
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DEBUG: bool = True
    # Настройки приложения
    PROJECT_NAME: str = "Fashion Eco"
    
    # class Config:
    #     env_file = ".env"

settings = Settings()

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# def get_db_url():
#     return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
#             f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

def get_db_url():
    return settings.DATABASE_URL