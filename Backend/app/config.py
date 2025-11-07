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

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Настройки БД
    DATABASE_URL: str = "sqlite:///./db/fashion_echo.db"
    
    # JWT настройки
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Настройки приложения
    PROJECT_NAME: str = "Fashion Echo"
    
    class Config:
        env_file = ".env"

settings = Settings()