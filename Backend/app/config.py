from __future__ import annotations

from pathlib import Path
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "db" / "fashion_eco.db"


class Settings(BaseSettings):
    # --- БАЗА ДАННЫХ ---
    DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_PATH}"

    # --- JWT ---
    SECRET_KEY: str = "change_me_in_prod"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- РЕЖИМЫ ---
    ENVIRONMENT: str = "development"  # development | testing | production
    DEBUG: bool = True

    # --- CORS ---
    # Разрешаем как строку, так и список, чтобы .env мог быть "a,b" или ["a","b"]
    CORS_ORIGINS: Union[str, List[str]] = ""

    # --- RATE LIMIT ---
    RATE_LIMIT: int = 100
    RATE_WINDOW_SECONDS: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def normalize_cors_origins(cls, v):
        """
        Нормализуем CORS_ORIGINS к списку строк:
        - "" или None -> дефолт для dev
        - "a,b,c" -> ["a","b","c"]
        - '["a","b"]' (валидный JSON) -> оставляем, pydantic сам приведёт к list[str]
        - уже list/tuple -> в list
        """
        if v is None or v == "":
            return ["http://localhost:3000", "http://127.0.0.1:3000"]

        # если уже список/кортеж — ок
        if isinstance(v, (list, tuple)):
            return list(v)

        # если пришла строка — пробуем два формата:
        if isinstance(v, str):
            s = v.strip()
            # если это JSON-строка со списком — пускай pydantic сам распарсит
            if s.startswith("[") and s.endswith("]"):
                return s
            # иначе — это строка с запятыми
            return [x.strip() for x in s.split(",") if x.strip()]

        return v

    def get_cors_origins(self) -> list[str]:
        """
        Унифицированный доступ для main.py.
        Возвращает список доменов CORS.
        """
        v = self.CORS_ORIGINS
        # если валидатор уже привёл к list[str] — просто вернём
        if isinstance(v, list):
            return v
        # если вдруг осталось строкой через запятую
        return [x.strip() for x in str(v).split(",") if x.strip()]



settings = Settings()


def get_db_url():
    return settings.DATABASE_URL
