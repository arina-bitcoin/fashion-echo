from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from Backend.app.core.database import create_db_and_tables
from Backend.app.config import settings
from Backend.app.api.api import api_router
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from Backend.app.core.exceptions import FashionEchoException  # <- наш базовый эксепшн

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path (как у тебя было)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске: создаем таблицы
    await create_db_and_tables()
    print("✅ Database tables created successfully")
    yield
    # При остановке: закрываем соединения
    print("🔴 Application shutting down")

app = FastAPI(
    title="Fashion Eco API",
    description="API для покупки, продажи и обмена одежды",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG
)


# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000",
                   "http://127.0.0.1:3000",
                   "http://[::1]:3000"],  # URL вашего фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

app.mount("/static", StaticFiles(directory="file_storage"), name="static")

# Добавьте обработчик ошибок для гарантии CORS headers
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
    # Принудительно добавляем CORS headers
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


# ---- Глобальный обработчик наших доменных ошибок ----
@app.exception_handler(FashionEchoException)
async def fashion_echo_exception_handler(
    request: Request,
    exc: FashionEchoException
):
    """
    Преобразует наши кастомные исключения в единый JSON-ответ.
    """
    return JSONResponse(
        status_code=400,  # можно позже дифференцировать по exc.code
        content={
            "error": exc.code,
            "message": exc.message,
        },
    )


# ---- Роуты ----
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Fashion Echo API with SQLite"}

