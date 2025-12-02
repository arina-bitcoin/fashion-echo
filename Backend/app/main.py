# from contextlib import asynccontextmanager
# from fastapi import FastAPI
# from Backend.app.api.api import api_router
#
#
# import sys
# from pathlib import Path
#
# # Добавляем текущую директорию в путь Python
# # sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, str(Path(__file__).parent.parent.parent))
#
# app = FastAPI(
#     title="Fashion Eco API",
#     description="API для покупки, продажи и обмена одежды",
#     version="1.0.0",
#     # lifespan=lifespan,
#     # debug=settings.DEBUG
# )
#
#
# # Настройка подключения фронтенда и бэкенда
# from fastapi.middleware.cors import CORSMiddleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],  # URL вашего фронтенда
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
#
#
# app.include_router(api_router, prefix="/api")
#
# @app.get("/")
# async def root():
#     return {"message": "Fashion Echo API with SQLite"}
#

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import sys
from pathlib import Path

from Backend.app.api.api import api_router
from Backend.app.core.exceptions import FashionEchoException  # <- наш базовый эксепшн

# Добавляем корень проекта в sys.path (как у тебя было)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

app = FastAPI(
    title="Fashion Eco API",
    description="API для покупки, продажи и обмена одежды",
    version="1.0.0",
)


# ---- CORS ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # фронтенд URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
