from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from Backend.app.core.database import get_db
from Backend.app.dependencies import get_current_user
from Backend.app.models.user import User
from Backend.app.schemas.ad import AdResponse, AdCreate, AdUpdate
from Backend.app.services.ad_service import AdService

router = APIRouter()

@router.get("/", response_model=List[AdResponse])
async def get_ads(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить список объявлений с фильтрацией"""
    return AdService.get_ads(db, skip=skip, limit=limit, type=type, category=category)

@router.post("/", response_model=AdResponse)
async def create_ad(
    ad_data: AdCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новое объявление"""
    return AdService.create_ad(db, ad_data, current_user.id)

@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(ad_id: int, db: Session = Depends(get_db)):
    """Получить объявление по ID"""
    ad = AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad