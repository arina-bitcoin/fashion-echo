from pathlib import Path
import uuid
import aiofiles
import aiofiles.os
from typing import Optional, Any
from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    File,
    UploadFile,
    Form,
    Body
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, cast, String

from Backend.app.core.database import get_db
from Backend.app.dependencies import get_current_user, get_current_user_optional, is_admin_user
from Backend.app.models.user import User
from Backend.app.models.ad import Ad
from Backend.app.schemas.ad import (
    AdResponse, 
    AdStatusResponse,
    AdCreate, 
    AdUpdate,
    AdStatus,
    AdType,
    AdSearch,
    Condition,
    SortBy,
    FavoriteResponse,
    ImageUploadResponse,
    ImageOrderUpdate
)
from Backend.app.services.ad_service import AdService
from Backend.app.utils.validators import validate_image_file

router = APIRouter()

# ---------- Объявления (публичные) ----------

@router.get("/", response_model=list[AdResponse])
async def get_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="Статус объявления: active, inactive"),
    type: Optional[str] = Query(None, regex="^(sell|buy|exchange)$"),
    main_category: Optional[str] = Query(None, description="Основная категория"),
    main_categories: Optional[list[str]] = Query(None, description="Основные категории (массив)"),
    sub_category: Optional[str] = Query(None, description="Подкатегория"),
    season: Optional[str] = Query(None, description="Сезон"),
    condition: Optional[str] = Query(None, description="Состояние товара"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    size: Optional[str] = Query(None, description="Размер"),
    color: Optional[str] = Query(None, description="Цвет"),
    search: Optional[str] = Query(None, description="Текстовый поиск"),
    sort: Optional[str] = Query("newest", description="Сортировка: newest, oldest, price_asc, price_desc, popular"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Получить список объявлений с фильтрацией"""
    
    # Для неавторизованных пользователей показываем только активные
    if not current_user:
        status = "active"

    categories_to_filter = main_categories if main_categories is not None else ([main_category] if main_category else None)
    
    return await AdService.get_ads(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        main_category=categories_to_filter,
        sub_category=sub_category,
        season=season,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        size=size,
        color=color,
        search=search,
        sort=sort
    )


@router.get("/{ad_id}", response_model=AdResponse)
async def get_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Получить объявление по ID"""
    ad = await AdService.get_ad(db, ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    # Проверяем активность
    if ad.status != AdStatus.ACTIVE and (not current_user or (current_user.id != ad.user_id and not current_user.is_admin)):
        raise HTTPException(status_code=404, detail="Объявление не найдено или недоступно")
    
    # Увеличиваем счетчик просмотров
    if ad.status == AdStatus.ACTIVE:
        await AdService.increment_view_count(db, ad_id)
    
    # Добавляем информацию об избранном для авторизованных пользователей
    if current_user:
        is_fav = await AdService.is_favorite(db, ad_id, current_user.id)
        setattr(ad, 'is_favorite', is_fav)
    
    # Pydantic будет обрабатывать преобразование images через model_validator
    # Не трогаем SQLAlchemy объекты напрямую
    
    return ad


@router.post("/search", response_model=list[AdResponse])
async def search_ads(
    search_data: AdSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Расширенный поиск объявлений"""
    # Обновляем skip и limit из query параметров, если они переданы
    if skip > 0:
        search_data.skip = skip
    if limit != 100:
        search_data.limit = limit
    
    result = await AdService.advanced_search(db, search_data)
    return result["ads"]


@router.post("/search/advanced", response_model=dict[str, Any])
async def advanced_search(
    search_data: AdSearch,
    db: AsyncSession = Depends(get_db),
):
    """
    Расширенный поиск объявлений со всеми фильтрами
    
    Пример тела запроса:
    {
        "status": "active",
        "ad_type": "sell",
        "main_categories": ["men", "women"],
        "sub_categories": ["shoes", "casual"],
        "seasons": ["winter", "autumn"],
        "min_price": 1000,
        "max_price": 5000,
        "conditions": ["new", "like_new"],
        "sizes": ["M", "L", "42"],
        "colors": ["black", "blue"],
        "query": "кожаные ботинки",
        "sort_by": "price_asc",
        "skip": 0,
        "limit": 20
    }
    """
    result = await AdService.advanced_search(db, search_data)
    
    # Добавляем is_favorite для авторизованных пользователей
    current_user = await get_current_user_optional(db)
    if current_user:
        for ad in result["ads"]:
            is_fav = await AdService.is_favorite(db, ad.id, current_user.id)
            setattr(ad, 'is_favorite', is_fav)
    
    return result


@router.get("/search/quick", response_model=list[AdResponse])
async def quick_search(
    # Параметры из query string для быстрого поиска
    q: Optional[str] = Query(None, description="Текстовый поиск"),
    category: Optional[str] = Query(None, description="Основная категория"),
    price_min: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    price_max: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    sort: Optional[str] = Query("newest", description="Сортировка"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество на странице"),
    db: AsyncSession = Depends(get_db),
):
    """
    Быстрый поиск через query параметры
    GET /ads/search/quick?q=куртка&category=men&price_min=1000&sort=price_asc&page=1
    """
    # Преобразуем в объект AdSearch
    # Преобразуем строку sort в SortBy enum
    sort_by_enum = None
    if sort:
        try:
            sort_by_enum = SortBy(sort)
        except ValueError:
            sort_by_enum = SortBy.NEWEST
    
    search_data = AdSearch(
        query=q,
        main_categories=[category] if category else None,
        min_price=price_min,
        max_price=price_max,
        sort_by=sort_by_enum or SortBy.NEWEST,
        skip=(page - 1) * per_page,
        limit=per_page
    )
    
    result = await AdService.advanced_search(db, search_data)
    return result["ads"]


@router.get("/filters/options")
async def get_filter_options(
    db: AsyncSession = Depends(get_db),
):
    """
    Получить все доступные опции для фильтров
    """
    options = await AdService.get_filter_options(db)
    return options


@router.get("/filters/suggest")
async def get_filter_suggestions(
    field: str = Query(..., description="Поле для автодополнения"),
    query: str = Query("", description="Запрос для поиска"),
    limit: int = Query(10, ge=1, le=50, description="Лимит предложений"),
    db: AsyncSession = Depends(get_db),
):
    """
    Автодополнение для полей фильтров
    GET /ads/filters/suggest?field=sizes&query=M&limit=10
    """
    
    if field == "sizes":
        stmt = select(
            func.distinct(Ad.size)
        ).where(
            Ad.size.isnot(None),
            Ad.size != '',
            Ad.size.ilike(f"%{query}%"),
            Ad.status == AdStatus.ACTIVE
        ).order_by(Ad.size).limit(limit)
        
    elif field == "colors":
        # Для SQLite
        stmt = select(
            func.distinct(Ad.colors)
        ).where(
            Ad.colors.isnot(None),
            cast(Ad.colors, String).ilike(f'%"{query}%"'),
            Ad.status == AdStatus.ACTIVE
        ).limit(limit)
    
    elif field == "main_categories":
        stmt = select(
            func.distinct(Ad.main_category)
        ).where(
            Ad.main_category.isnot(None),
            cast(Ad.main_category, String).ilike(f"%{query}%"),
            Ad.status == AdStatus.ACTIVE
        ).order_by(Ad.main_category).limit(limit)
    
    else:
        raise HTTPException(status_code=400, detail="Неподдерживаемое поле")
    
    result = await db.execute(stmt)
    suggestions = [row[0] for row in result.all() if row[0]]
    
    return {"field": field, "suggestions": suggestions}

# ---------- Объявления (авторизованные) ----------

@router.post("/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(
    ad_data: AdCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новое объявление"""
    
    print(f"📤 Создание объявления: {ad_data.title}")
    print(f"📤 Данные объявления: {ad_data.model_dump()}")
    
    ad = await AdService.create_ad(db, ad_data, current_user.id)
    
    return ad


@router.put("/{ad_id}", response_model=AdResponse)
async def update_ad(
    ad_id: int,
    ad_data: AdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить объявление (только владелец)"""
    print(f"📤 Данные для обновления объявления {ad_id}: {ad_data.model_dump()}")
    print(f"📤 Тип данных: {type(ad_data)}")
    
    ad = await AdService.update_ad(db, ad_id, current_user.id, ad_data)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found or you don't have permission")
    
    return ad


@router.patch("/{ad_id}", response_model=AdResponse)
async def update_ad_partial(
    ad_id: int,
    ad_data: AdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Частичное обновление объявления (PATCH)"""
    ad = await AdService.update_ad(
        db=db,
        ad_id=ad_id,
        user_id=current_user.id,
        ad_data=ad_data,
        is_admin=current_user.is_admin
    )
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено или нет прав доступа")
    return ad


# УДАЛЕН НЕПРАВИЛЬНЫЙ ЭНДПОИНТ @router.post("/upload-image") - он некорректный

@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: int,
    soft_delete: bool = Query(False, description="Физическое удаление (is_active=False)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить объявление"""
    success = await AdService.delete_ad(
        db=db,
        ad_id=ad_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin,
        soft_delete=soft_delete
    )
    if not success:
        raise HTTPException(status_code=404, detail="Объявление не найдено или нет прав доступа")


@router.post("/{ad_id}/activate", response_model=AdStatusResponse)
async def activate_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Активировать объявление"""
    # Находим объявление
    stmt = select(Ad).where(Ad.id == ad_id)
    result = await db.execute(stmt)
    ad = result.scalar_one_or_none()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    # Проверяем права доступа
    if not current_user.is_admin and ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    
    # Активируем
    ad.status = AdStatus.ACTIVE
    ad.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    # await db.refresh(ad)
    
    return {
            "message": "Объявление активировано",
            "ad_id": ad_id,
            "status": "active"
        }

@router.post("/{ad_id}/deactivate", response_model=AdStatusResponse)
async def deactivate_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Деактивировать объявление"""
    # Находим объявление
    stmt = select(Ad).where(Ad.id == ad_id)
    result = await db.execute(stmt)
    ad = result.scalar_one_or_none()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    
    # Проверяем права доступа
    if not current_user.is_admin and ad.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Нет прав доступа")
    
    # Деактивируем
    ad.status = AdStatus.INACTIVE
    ad.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    # await db.refresh(ad)
    return {
        "message": "Объявление деактивировано",
        "ad_id": ad_id,
        "status": "inactive"
    }

# ---------- Избранное ----------

@router.post("/{ad_id}/favorite", response_model=FavoriteResponse)
async def add_to_favorites(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Добавить объявление в избранное"""
    success = await AdService.add_to_favorites(db, ad_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Объявление уже в избранном или не существует"
        )
    
    return FavoriteResponse(
        ad_id=ad_id,
        user_id=current_user.id,
        added=True,
        message="Объявление добавлено в избранное"
    )


@router.delete("/{ad_id}/favorite", response_model=FavoriteResponse)
async def remove_from_favorites(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить объявление из избранного"""
    success = await AdService.remove_from_favorites(db, ad_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Объявление не найдено в избранном"
        )
    
    return FavoriteResponse(
        ad_id=ad_id,
        user_id=current_user.id,
        added=False,
        message="Объявление удалено из избранного"
    )


@router.get("/favorites/", response_model=list[AdResponse])
async def get_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить избранные объявления"""
    ads = await AdService.get_favorite_ads(db, current_user.id, skip, limit)
    
    # Помечаем все как избранные
    for ad in ads:
        setattr(ad, 'is_favorite', True)
    
    return ads


# ---------- Управление изображениями ----------

@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Загрузить изображение (отдельно от объявления)"""
    # Валидация файла
    validate_image_file(file)
    
    # Сохраняем файл
    upload_dir = Path("media") / "ads"
    await aiofiles.os.makedirs(upload_dir, exist_ok=True)
    
    # Генерируем уникальное имя
    ext = Path(file.filename).suffix.lower() or ".jpg"
    if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        ext = ".jpg"
    
    new_name = f"{uuid.uuid4().hex}{ext}"
    dest_path = upload_dir / new_name
    
    # Асинхронное сохранение
    async with aiofiles.open(dest_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)
    
    # Возвращаем информацию о файле
    relative_path = f"media/ads/{new_name}"
    
    return ImageUploadResponse(
        file_path=str(dest_path),
        filename=new_name,
        url=f"/{relative_path}",
        size=dest_path.stat().st_size if dest_path.exists() else 0
    )


@router.post("/{ad_id}/images", response_model=list[ImageUploadResponse])
async def upload_multiple_images(
    ad_id: int,
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Загрузить несколько изображений для объявления"""
    if len(files) > 10:
        raise HTTPException(
            status_code=400, 
            detail="Максимальное количество файлов: 10"
        )
    
    uploaded_images = []
    
    for file in files:
        # Валидация
        validate_image_file(file)
        
        # Сохраняем файл
        upload_dir = Path("media") / "ads"
        await aiofiles.os.makedirs(upload_dir, exist_ok=True)
        
        ext = Path(file.filename).suffix.lower() or ".jpg"
        if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            ext = ".jpg"
        
        new_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = upload_dir / new_name
        
        async with aiofiles.open(dest_path, "wb") as buffer:
            content = await file.read()
            await buffer.write(content)
        
        # Добавляем в базу данных
        image = await AdService.add_image_to_ad(
            db=db,
            ad_id=ad_id,
            image_path=str(dest_path),
            user_id=current_user.id,
            is_admin=current_user.is_admin
        )
        
        if image:
            relative_path = f"media/ads/{new_name}"
            uploaded_images.append(ImageUploadResponse(
                file_path=str(dest_path),
                filename=new_name,
                url=f"/{relative_path}",
                size=dest_path.stat().st_size if dest_path.exists() else 0,
                image_id=image.id
            ))
    
    return uploaded_images


@router.delete("/images/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    filename: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Удалить изображение"""
    success = await AdService.delete_image(
        db=db,
        filename=filename,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Изображение не найдено или нет прав доступа"
        )


@router.put("/{ad_id}/images/order", status_code=status.HTTP_200_OK)
async def update_image_order(
    ad_id: int,
    order_data: ImageOrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Обновить порядок изображений"""
    success = await AdService.update_image_order(
        db=db,
        ad_id=ad_id,
        image_ids=order_data.image_ids,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    if not success:
        raise HTTPException(
            status_code=404, 
            detail="Объявление не найдено или нет прав доступа"
        )
    
    return {"message": "Порядок изображений обновлен"}


@router.get("/{ad_id}/images", response_model=list[ImageUploadResponse])
async def get_ad_images(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить изображения объявления"""
    images = await AdService.get_ad_images(db, ad_id)
    
    result = []
    for image in images:
        file_path = Path(image.file_path)
        if file_path.exists():
            result.append(ImageUploadResponse(
                file_path=str(file_path),
                filename=file_path.name,
                url=f"/{image.file_path}",
                size=file_path.stat().st_size,
                image_id=image.id,
                order=image.order
            ))
    
    return result


# ---------- Статистика ----------

@router.get("/{ad_id}/stats")
async def get_ad_stats(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Получить статистику объявления"""
    stats = await AdService.get_ad_stats(
        db=db,
        ad_id=ad_id,
        user_id=current_user.id,
        is_admin=current_user.is_admin
    )
    if not stats:
        raise HTTPException(
            status_code=404, 
            detail="Объявление не найдено или нет прав доступа"
        )
    
    return stats