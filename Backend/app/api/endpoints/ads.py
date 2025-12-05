from pathlib import Path
import uuid
import shutil
from typing import Optional, List

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    File,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from Backend.app.core.database import get_db
from Backend.app.dependencies import get_current_user
from Backend.app.models.user import User
from Backend.app.schemas.ad import AdResponse, AdCreate, AdUpdate
from Backend.app.services.ad_service import AdService
from Backend.app.utils.validators import validate_image_file

router = APIRouter()


# ---------- Объявления ----------

@router.get("/", response_model=List[AdResponse])
async def get_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="all, active, inactive"),
    type: Optional[str] = Query(None, description="sell, exchange, buy_request"),
    main_categories: Optional[List[str]] = Query(None, description="men, women, kids, unisex, baby"),
    subcategories: Optional[List[str]] = Query(None, description="formal, casual, sports, outerwear, underwear, swimwear, accessories, shoes, bags, jewelry"),
    seasons: Optional[List[str]] = Query(None, description="winter, spring, summer, autumn, all_season"),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    condition: Optional[List[str]] = Query(None, description="new, like_new, excellent, good, satisfactory, needs_repair"),
    sizes: Optional[List[str]] = Query(None),
    colors: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None, description="Текстовый поиск"),
    sort: Optional[str] = Query("newest", description="newest, oldest, price_asc, price_desc, popular"),
    db: AsyncSession = Depends(get_db),
):
    """Получить список объявлений с фильтрацией"""
    return await AdService.get_ads(
        db,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        main_categories=main_categories,
        subcategories=subcategories,
        seasons=seasons,
        min_price=min_price,
        max_price=max_price,
        condition=condition,
        sizes=sizes,
        colors=colors,
        search=search,
        sort=sort,
    )


@router.post("/", response_model=AdResponse)
async def create_ad(
    ad_data: AdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новое объявление"""
    # Логируем входящие данные для отладки
    import json
    print(f"📤 Создание объявления с изображениями: {json.dumps(ad_data.images, indent=2) if ad_data.images else 'Нет изображений'}")
    
    ad = await AdService.create_ad(db, ad_data, current_user.id)
    
    # Логируем сохраненные изображения
    print(f"✅ Объявление создано. Сохраненные изображения: {json.dumps(ad.images if ad.images else [], indent=2)}")
    
    return ad


@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(ad_id: int, db: AsyncSession = Depends(get_db)):
    """Получить объявление по ID"""
    ad = await AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad


@router.put("/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: int,
    ad_data: AdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить объявление (только владелец)"""
    ad_dict = ad_data.dict(exclude_unset=True)
    
    if not ad_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    ad = await AdService.update_ad(db, ad_id, current_user.id, ad_dict)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found or you don't have permission")
    
    return ad


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить объявление (только владелец)"""
    success = await AdService.delete_ad(db, ad_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Ad not found or you don't have permission")
    
    return None


# ---------- Загрузка изображений ----------

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),  # ВАЖНО: имя параметра file
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Загрузка изображения объявления.

    Ожидается multipart/form-data с ключом "file".
    При невалидном типе файла validate_image_file выбросит ValidationException,
    а глобальный обработчик вернёт 400.
    """
    # Валидация типа и размера
    validate_image_file(file)

    # Папка для картинок объявлений (сохраняем в File_storage для статической раздачи)
    # Проверяем корень проекта (на уровень выше Backend)
    project_root = Path(__file__).parent.parent.parent.parent
    upload_dir = project_root / "File_storage" / "ads"
    if not upload_dir.exists():
        upload_dir = project_root / "Backend" / "file_storage" / "ads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Генерируем уникальное имя файла
    ext = Path(file.filename).suffix or ".jpg"
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = upload_dir / new_name

    # Сохраняем файл
    with dest_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Возвращаем относительный путь от file_storage для использования в статической раздаче
    relative_path = f"ads/{new_name}"
    
    return {
        "file_path": relative_path,
        "filename": new_name,
    }


# Дополнительный отладочный эндпоинт (по желанию)
@router.post("/debug/upload-image")
async def debug_upload_image(file: UploadFile = File(...)):
    validate_image_file(file)
    return {"filename": file.filename, "content_type": file.content_type}
