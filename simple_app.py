"""
Простое FastAPI приложение для демонстрации Docker setup
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Fashion Eco API",
    description="Платформа экологичной моды",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "Fashion Eco API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if os.getenv("DATABASE_URL") else "not configured",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

@app.get("/api/ads/")
async def get_ads():
    """Получить список объявлений"""
    return {
        "items": [
            {
                "id": 1,
                "title": "Джинсы Levi's",
                "price": 2000,
                "description": "Винтажные джинсы в отличном состоянии"
            },
            {
                "id": 2,
                "title": "Куртка кожаная",
                "price": 5000,
                "description": "Натуральная кожа, размер M"
            }
        ],
        "total": 2
    }

@app.get("/api/ads/{ad_id}")
async def get_ad(ad_id: int):
    """Получить объявление по ID"""
    return {
        "id": ad_id,
        "title": f"Объявление #{ad_id}",
        "price": 1000,
        "description": "Описание объявления"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)