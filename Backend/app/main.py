from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import sys
from pathlib import Path

# Добавляем корень проекта в sys.path для импортов
# Если запускается из корня: fashion-echo/Backend/app/main.py -> fashion-echo/
# Если запускается из Backend: Backend/app/main.py -> Backend/.. (т.е. fashion-echo/)
current_file = Path(__file__).resolve()
# Получаем корень проекта (3 уровня вверх от main.py: app -> Backend -> fashion-echo)
project_root = current_file.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from Backend.app.core.database import create_db_and_tables
from Backend.app.config import settings

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
# Разрешаем origins для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://[::1]:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Кэширование preflight запросов
)

# Middleware для логирования запросов (для отладки)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    origin = request.headers.get("origin", "No origin")
    print(f"🌐 {request.method} {request.url.path} - Origin: {origin}")
    try:
        response = await call_next(request)
        # Убеждаемся, что CORS заголовки есть в ответе
        if origin and origin in ["http://localhost:3000", "http://127.0.0.1:3000", "http://[::1]:3000"]:
            if "Access-Control-Allow-Origin" not in response.headers:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
        print(f"✅ {request.method} {request.url.path} - Status: {response.status_code}")
        return response
    except Exception as e:
        print(f"❌ Error in {request.method} {request.url.path}: {e}")
        raise

from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException
from Backend.app.api.api import api_router
from Backend.app.core.exceptions import FashionEchoException  # <- наш базовый эксепшн

# Путь к статическим файлам (относительно корня проекта или абсолютный)
# Сначала проверяем File_storage в корне проекта (там находятся файлы)
static_dir = project_root / "File_storage"
if not static_dir.exists():
    static_dir = project_root / "Backend" / "file_storage"  # Альтернативный путь

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    print(f"✅ Static files mounted from: {static_dir}")
else:
    print(f"⚠️ Static files directory not found: {static_dir}")

# Функция для добавления CORS заголовков
def add_cors_headers(response: JSONResponse, origin: str = None):
    """Добавляет CORS заголовки к ответу"""
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://[::1]:3000",
    ]
    if origin and origin in allowed_origins:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Expose-Headers"] = "*"
    return response

# Обработчик для FastAPI HTTPException
@app.exception_handler(FastAPIHTTPException)
async def fastapi_http_exception_handler(request: Request, exc: FastAPIHTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    origin = request.headers.get("origin")
    return add_cors_headers(response, origin)

# Обработчик для Starlette HTTPException
@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    origin = request.headers.get("origin")
    return add_cors_headers(response, origin)

# Обработчик для всех остальных исключений
@app.exception_handler(Exception)
async def universal_exception_handler(request: Request, exc: Exception):
    import traceback
    print(f"❌ Unhandled exception: {exc}")
    traceback.print_exc()
    
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
    origin = request.headers.get("origin")
    return add_cors_headers(response, origin)


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
        status_code=400,  # можно позже дифференцировать по exc.code
        content={
            "error": exc.code,
            "message": exc.message,
        },
    )
    origin = request.headers.get("origin")
    return add_cors_headers(response, origin)


# ---- Роуты ----
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Fashion Echo API with SQLite"}

