from fastapi import APIRouter
from Backend.app.api.endpoints import auth, users, ads, secondhand
from Backend.app.services import auth_service
from Backend.app.api.endpoints.health import router as health_router

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ads.router, prefix="/ads", tags=["advertisement"])
api_router.include_router(secondhand.router, prefix="/secondhand", tags=["secondhand shop"])
api_router.include_router(health_router)
