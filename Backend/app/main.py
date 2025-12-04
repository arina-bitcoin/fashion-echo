from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from Backend.app.core.database import create_db_and_tables
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from Backend.app.config import settings
from Backend.app.models.ad import Ad
from Backend.app.models.user import User
from Backend.app.models.secondhand import Secondhand


import sys
from pathlib import Path
import traceback

# Добавляем корень проекта в sys.path (как у тебя было)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # При запуске: создаем таблицы
    await create_db_and_tables()

    # Выполняем миграции
    from Backend.app.core.migrations import migrate_database
    try:
        await migrate_database()
    except Exception as e:
        print(f"⚠️ Миграция не выполнена: {e}")

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

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://[::1]:3000"
]

# ---- CORS Middleware ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Middleware для принудительного добавления CORS заголовков ко ВСЕМ ответам ----
@app.middleware("http")
async def add_cors_headers_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
    except Exception as exc:
        # Если произошло необработанное исключение
        print(f"❌ Unhandled exception in middleware: {exc}")
        print(traceback.format_exc())
        
        response = JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "Внутренняя ошибка сервера"
            }
        )
    
    # Добавляем CORS заголовки ко всем ответам (успешным и ошибкам)
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    # Обязательные CORS заголовки для preflight запросов
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    
    return response

from fastapi.staticfiles import StaticFiles
from Backend.app.core.exceptions import FashionEchoException  # <- наш базовый эксепшн

app.mount("/static", StaticFiles(directory="file_storage"), name="static")

# ---- Глобальный обработчик наших доменных ошибок ----
@app.exception_handler(FashionEchoException)
async def fashion_echo_exception_handler(
    request: Request,
    exc: FashionEchoException
):
    """
    Преобразует наши кастомные исключения в единый JSON-ответ.
    """
    response = JSONResponse(
        status_code=exc.status_code if hasattr(exc, 'status_code') else 400,
        content={
            "error": exc.code,
            "message": exc.message,
        }
    )
    
    # Добавляем CORS заголовки
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# ---- Обработчик ошибок валидации ----
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    response = JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Ошибка валидации данных",
            "details": exc.errors()
        }
    )
    
    # Добавляем CORS заголовки
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# ---- Обработчик HTTP исключений (404, 401, etc) ----
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
):
    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": str(exc.detail) if hasattr(exc, 'detail') else "HTTP ошибка",
        }
    )
    
    # Добавляем CORS заголовки
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# ---- Обработчик всех остальных исключений ----
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    # Логируем ошибку для отладки
    print(f"❌ Unhandled exception: {exc}")
    print(traceback.format_exc())
    
    response = JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "Внутренняя ошибка сервера"
        }
    )
    
    # Добавляем CORS заголовки
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    
    return response

# ---- Роуты ----
from Backend.app.api.api import api_router

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Fashion Echo API with SQLite"}