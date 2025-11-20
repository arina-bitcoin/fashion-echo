# from fastapi import APIRouter, Depends, HTTPException, Query, status
# from sqlalchemy.orm import Session
# from typing import Optional, List

# from Backend.app.core.database import get_db
# from Backend.app.dependencies import get_current_user
# from Backend.app.models.user import User
# from Backend.app.schemas.secondhand import ...
# from Backend.app.services.ad_service import AdService

# router = APIRouter()

# @router.get("/", response_model=List[SecondhandResponse])
# async def get_secondhands(
#     city: Optional[str] = None,
#     search: Optional[str] = None,
#     db: Session = Depends(get_db)
# ):
#     pass

# @router.get("/map", response_model=List[MapPointResponse])
# async def get_secondhands_for_map(
#     ne_lat: float, ne_lng: float, sw_lat: float, sw_lng: float,
#     db: Session = Depends(get_db)
# ):
#     pass

# backend/app/api/v1/endpoints/secondhand.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from Backend.app.core.database import get_db
from Backend.app.models.secondhand import Secondhand
from Backend.app.schemas.secondhand import (
    SecondhandCreate, 
    SecondhandUpdate, 
    SecondhandResponse,
    MapPointResponse,
    SecondhandSearchResponse,
    SecondhandFilters,
    MapBoundsFilters
)
from Backend.app.services.secondhand_service import SecondhandService

router = APIRouter()
secondhand_service = SecondhandService()

@router.get("/", response_model=SecondhandSearchResponse)
async def get_secondhands(
    city: Optional[str] = Query(None, description="Фильтр по городу"),
    search: Optional[str] = Query(None, description="Поиск по названию или адресу"),
    is_active: Optional[bool] = Query(True, description="Только активные"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Получить список секондхендов с фильтрацией
    """
    filters = SecondhandFilters(
        city=city,
        search=search,
        is_active=is_active
    )
    
    items, total = secondhand_service.get_secondhands(db, filters, skip, limit)
    
    return SecondhandSearchResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/map", response_model=List[MapPointResponse])
async def get_secondhands_for_map(
    bounds: MapBoundsFilters = Depends(),
    db: Session = Depends(get_db)
):
    """
    Получить секондхенды для отображения на карте
    """
    secondhands = secondhand_service.get_secondhands_in_bounds(
        db, 
        bounds.ne_lat, bounds.ne_lng, 
        bounds.sw_lat, bounds.sw_lng
    )
    return secondhands


@router.post("/", response_model=SecondhandResponse)
async def create_secondhand(
    secondhand_data: SecondhandCreate,
    db: Session = Depends(get_db)
):
    """
    Создать новый секондхенд (для админов)
    """
    return secondhand_service.create_secondhand(db, secondhand_data)


@router.get("/{secondhand_id}", response_model=SecondhandResponse)
async def get_secondhand(
    secondhand_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить детальную информацию о секондхенде
    """
    secondhand = secondhand_service.get_secondhand_by_id(db, secondhand_id)
    if not secondhand:
        raise HTTPException(status_code=404, detail="Secondhand not found")
    return secondhand


@router.put("/{secondhand_id}", response_model=SecondhandResponse)
async def update_secondhand(
    secondhand_id: int,
    secondhand_data: SecondhandUpdate,
    db: Session = Depends(get_db)
):
    """
    Обновить информацию о секондхенде (для админов)
    """
    updated = secondhand_service.update_secondhand(db, secondhand_id, secondhand_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Secondhand not found")
    return updated


@router.delete("/{secondhand_id}")
async def delete_secondhand(
    secondhand_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить секондхенд (мягкое удаление)
    """
    success = secondhand_service.delete_secondhand(db, secondhand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Secondhand not found")
    return {"message": "Secondhand deleted successfully"}