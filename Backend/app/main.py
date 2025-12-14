from __future__ import annotations

import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from Backend.app.config import settings
from Backend.app.core.database import create_db_and_tables
from Backend.app.core.rate_limiting import RateLimiterMiddleware
from Backend.app.core.security_headers import SecurityHeadersMiddleware
from Backend.app.core.exceptions import FashionEchoException

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
    
    # Инициализируем тестовые данные секондхендов
    await initialize_secondhands_data()
    
    yield
    # При остановке
    print("🔴 Application shutting down")

async def initialize_secondhands_data():
    """Инициализация тестовых данных секондхендов при запуске"""
    try:
        from Backend.app.core.database import engine
        from Backend.app.core.initial_data import initialize_secondhands_sync
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        
        # Создаем синхронную сессию для инициализации (функция написана для синхронной работы)
        db_url = str(engine.url).replace('+aiosqlite', '')
        sync_engine = create_engine(db_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=sync_engine)
        
        with SessionLocal() as sync_db:
            initialize_secondhands_sync(sync_db)
                
    except Exception as e:
        print(f"⚠️ Ошибка при инициализации секондхендов: {e}")
        import traceback
        traceback.print_exc()

app = FastAPI(
    title="Fashion Eco API",
    description="API для покупки, продажи и обмена одежды",
    version="1.0.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://[::1]:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_cors_headers_middleware(request: Request, call_next):
    # Если это OPTIONS запрос, сразу возвращаем успешный ответ
    if request.method == "OPTIONS":
        response = JSONResponse(
            status_code=200,
            content={"message": "OK"}
        )
        origin = request.headers.get("origin")
        if origin in origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Origin, Accept"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 часа
        return response
    
    try:
        response = await call_next(request)
    except Exception as exc:
        print(f"❌ Unhandled exception in middleware: {exc}")
        print(traceback.format_exc())
        response = JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "message": "Внутренняя ошибка сервера"},
        )

    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"

    return response

# === СТАТИКА ===
app.mount("/static", StaticFiles(directory="file_storage"), name="static")

# === ГЛОБАЛЬНЫЕ ОБРАБОТЧИКИ ОШИБОК ===
@app.exception_handler(FashionEchoException)
async def fashion_echo_exception_handler(request: Request, exc: FashionEchoException):
    response = JSONResponse(
        status_code=getattr(exc, "status_code", 400),
        content={"error": exc.code, "message": exc.message},
    )
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    print(f"❌ Ошибка валидации для {request.method} {request.url.path}:")
    for error in errors:
        print(f"   - Поле: {error.get('loc', [])}, Ошибка: {error.get('msg', '')}, Тип: {error.get('type', '')}")
    response = JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Ошибка валидации данных",
            "details": errors,
        },
    )
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": str(getattr(exc, "detail", "HTTP ошибка"))},
    )
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    print(f"❌ Unhandled exception: {exc}")
    print(traceback.format_exc())
    response = JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "Внутренняя ошибка сервера"},
    )
    origin = request.headers.get("origin")
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response

from Backend.app.api.api import api_router

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Fashion Echo API with SQLite"}