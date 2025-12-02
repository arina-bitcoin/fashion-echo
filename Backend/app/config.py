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

    # Настройки приложения
    PROJECT_NAME: str = "Fashion Eco"
    DEBUG: bool = True

    # class Config:
    #     env_file = ".env"

settings = Settings()

def get_db_url():
    return settings.DATABASE_URL