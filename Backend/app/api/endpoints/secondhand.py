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
    MapBoundsFilters,
    MapClusterResponse
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

    item_models = [
        SecondhandResponse.model_validate(obj, from_attributes=True)
        for obj in items
    ]

    return SecondhandSearchResponse(
        items=item_models,
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
    Получить секондхенды для отображения на карте (простые точки).
    Возвращаем сразу Pydantic-модели, без ORM-магии.
    """
    secondhands = secondhand_service.get_secondhands_in_bounds(
        db,
        bounds.ne_lat,
        bounds.ne_lng,
        bounds.sw_lat,
        bounds.sw_lng,
    )

    points: List[MapPointResponse] = []

    for sh in secondhands:
        # защита от возможных None в координатах
        if sh.latitude is None or sh.longitude is None:
            continue

        points.append(
            MapPointResponse(
                id=sh.id,
                name=sh.name,
                latitude=sh.latitude,
                longitude=sh.longitude,
                address=sh.address,
                phone=sh.phone,
            )
        )

    return points



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

# мое дополнение
@router.get("/map/clusters", response_model=List[MapClusterResponse])
async def get_map_clusters(
    zoom: int = Query(..., ge=0, le=20, description="Текущий zoom карты"),
    bounds: MapBoundsFilters = Depends(),
    db: Session = Depends(get_db)
):
    """
    Кластеры секондхендов для карты на основании zoom + границ видимой области.
    """
    clusters = secondhand_service.get_clusters_in_bounds(
        db=db,
        zoom=zoom,
        ne_lat=bounds.ne_lat,
        ne_lng=bounds.ne_lng,
        sw_lat=bounds.sw_lat,
        sw_lng=bounds.sw_lng,
    )
    return clusters


from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Backend.app.config import settings
from Backend.app.models.secondhand import Secondhand

# ...

@router.get("/debug/db")
async def debug_db():
    """
    Временный debug-эндпоинт: проверяет, с какой БД мы работаем,
    и сколько в ней записей secondhands.
    Использует отдельный sync-движок, НЕ get_db / SessionLocal.
    """
    # Берём тот же URL, что и у приложения, но делаем его sync-совместимым
    db_url = settings.DATABASE_URL
    if db_url.startswith("sqlite+aiosqlite"):
        db_url_sync = db_url.replace("sqlite+aiosqlite", "sqlite", 1)
    else:
        db_url_sync = db_url

    engine = create_engine(
        db_url_sync,
        connect_args={"check_same_thread": False},
        echo=True,
    )
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with Session() as db:
        count = db.query(Secondhand).count()

    return {
        "database_url": db_url,
        "database_url_sync": db_url_sync,
        "secondhands_count": count
    }

@router.get("/search", response_model=List[MapPointResponse])
async def search_secondhands_by_radius(
    lat: float = Query(..., description="Широта центра поиска"),
    lng: float = Query(..., description="Долгота центра поиска"),
    radius_km: float = Query(5, gt=0, description="Радиус в км"),
    db: Session = Depends(get_db),
):
    """
    Поиск секондхендов в радиусе от точки.
    Возвращаем упрощённый список точек для карты.
    """
    secondhands = secondhand_service.search_nearby(db, lat=lat, lng=lng, radius_km=radius_km)
    # Можно либо вернуть ORM-объекты (они сконвертятся в MapPointResponse),
    # либо явно собрать список словарей.
    return [
        MapPointResponse(
            id=s.id,
            name=s.name,
            latitude=s.latitude,
            longitude=s.longitude,
            address=s.address,
            phone=s.phone,
        )
        for s in secondhands
    ]

# временно
from Backend.app.core.exceptions import ValidationException

@router.get("/debug/error")
async def debug_error():
    # специально бросаем нашу доменную ошибку
    raise ValidationException("Test validation from debug endpoint")
