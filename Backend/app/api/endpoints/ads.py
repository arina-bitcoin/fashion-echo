from pathlib import Path
import uuid
import aiofiles
import aiofiles.os
from typing import Optional, Any
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    File,
    UploadFile,
    Form,
    Body,
    Query
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
    AdCreate, 
    AdUpdate,
    AdStatus,
    AdType,
    AdSearch,
    Condition,
    FavoriteResponse,
    ImageUploadResponse,
    ImageOrderUpdate
)
from Backend.app.services.ad_service import AdService
from Backend.app.utils.validators import validate_image_file
# from Backend.app.utils.file_upload import save_uploaded_file

router = APIRouter()

# ---------- Объявления (публичные) ----------

@router.get("/", response_model=list[AdResponse])
async def get_ads(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="Статус объявления: active, inactive"),
    type: Optional[str] = Query(None, regex="^(sell|buy|exchange)$"),
    main_category: Optional[str] = Query(None, description="Основная категория"),
    sub_category: Optional[str] = Query(None, description="Подкатегория"),
    season: Optional[str] = Query(None, description="Сезон"),
    condition: Optional[str] = Query(None, description="Состояние товара"),
    min_price: Optional[float] = Query(None, ge=0, description="Минимальная цена"),
    max_price: Optional[float] = Query(None, ge=0, description="Максимальная цена"),
    size: Optional[str] = Query(None, description="Размер"),
    color: Optional[str] = Query(None, description="Цвет"),
    query: Optional[str] = Query(None, description="Текстовый поиск"),
    sort: Optional[str] = Query("newest", description="Сортировка: newest, oldest, price_asc, price_desc, popular"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Получить список объявлений с фильтрацией"""
    
    # Для неавторизованных пользователей показываем только активные
    if not current_user:
        status = "active"
    
    return await AdService.get_ads(
        db=db,
        skip=skip,
        limit=limit,
        status=status,
        type=type,
        main_category=main_category,
        sub_category=sub_category,
        season=season,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        size=size,
        color=color,
        query=query,
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
    
    return ad


@router.post("/search", response_model=list[AdResponse])
async def search_ads(
    search_data: AdSearch,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Расширенный поиск объявлений"""
    return await AdService.search_ads(
        db=db,
        query=search_data.query,
        min_price=search_data.min_price,
        max_price=search_data.max_price,
        type=search_data.type,
        category=search_data.category,
        location=search_data.location,
        sort_by=search_data.sort_by or "newest",
        skip=skip,
        limit=limit
    )

# @router.post("/search/advanced", response_model=dict[str, Any])
# async def advanced_search(
#     search_data: AdSearch,
#     db: AsyncSession = Depends(get_db),
#     current_user: Optional[User] = Depends(get_current_user_optional)
# ):
#     """
#     Расширенный поиск объявлений со всеми фильтрами и сортировками
    
#     Примеры запросов:
    
#     1. Поиск мужских джинсов до 5000 руб:
#     {
#         "query": "джинсы",
#         "max_price": 5000,
#         "categories": {
#             "main_categories": ["mens"],
#             "subcategories": ["casual"]
#         },
#         "sorting": {
#             "sort_by": "price_asc"
#         }
#     }
    
#     2. Поиск женских платьев для лета:
#     {
#         "categories": {
#             "main_categories": ["womens"],
#             "subcategories": ["formal", "casual"],
#             "seasons": ["summer"]
#         },
#         "sorting": {
#             "sort": {
#                 "primary": "popular",
#                 "secondary": "newest"
#             }
#         }
#     }
    
#     3. Поиск детской зимней одежды:
#     {
#         "categories": {
#             "main_categories": ["kids"],
#             "subcategories": ["outerwear"],
#             "seasons": ["winter"]
#         },
#         "conditions": ["new", "like_new"],
#         "sorting": {
#             "sort_by": "price_desc"
#         }
#     }
#     """
#     result = await AdService.search_ads_comprehensive(db, search_data)
    
#     # Добавляем информацию об избранном для авторизованных пользователей
#     if current_user:
#         for ad in result["ads"]:
#             is_fav = await AdService.is_favorite(db, ad.id, current_user.id)
#             setattr(ad, 'is_favorite', is_fav)
    
#     return result

from fastapi import Query

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
    search_data = AdSearch(
        query=q,
        main_categories=[category] if category else None,
        min_price=price_min,
        max_price=price_max,
        sort_by=sort,
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
        # Для PostgreSQL
        if db.bind.dialect.name == 'postgresql':
            stmt = select(
                func.distinct(func.jsonb_array_elements_text(Ad.colors).label('color'))
            ).where(
                Ad.colors.isnot(None),
                func.jsonb_array_elements_text(Ad.colors).ilike(f"%{query}%"),
                Ad.status == AdStatus.ACTIVE
            ).order_by('color').limit(limit)
        else:
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



# @router.get("/categories/all", response_model=dict[str, list[str]])
# async def get_all_categories():
#     """
#     Получить все доступные категории для фильтрации
    
#     Возвращает:
#     {
#         "main_categories": ["mens", "womens", "kids", ...],
#         "subcategories": ["formal", "casual", "sports", ...],
#         "seasons": ["summer", "winter", ...],
#         "conditions": ["new", "like_new", ...],
#         "ad_types": ["sell", "buy", ...],
#         "sizes": ["XS", "S", "M", "L", "XL", ...],
#         "popular_brands": ["Zara", "H&M", ...],
#         "colors": ["black", "white", "blue", ...]
#     }
#     """
#     return {
#         "main_categories": [cat.value for cat in ClothingCategory if cat.value in [
#             "mens", "womens", "kids", "unisex", "baby"
#         ]],
#         "subcategories": [cat.value for cat in ClothingCategory if cat.value in [
#             "formal", "casual", "sports", "outerwear", "underwear",
#             "swimwear", "accessories", "shoes", "bags", "jewelry"
#         ]],
#         "seasons": [cat.value for cat in ClothingCategory if cat.value in [
#             "summer", "winter", "autumn", "spring", "all_season"
#         ]],
#         "conditions": [cond.value for cond in Condition],
#         "ad_types": [ad_type.value for ad_type in AdType],
#         "sizes": ["XS", "S", "M", "L", "XL", "XXL", "XXXL"],
#         "popular_brands": ["Zara", "H&M", "Nike", "Adidas", "Gucci", "Prada"],
#         "colors": ["black", "white", "red", "blue", "green", "yellow", "pink"]
#     }

# ---------- Объявления (авторизованные) ----------

# @router.post("/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
# async def create_ad(
#     type: str = Form(...),
#     title: str = Form(...),
#     description: Optional[str] = Form(None),
#     price: Optional[float] = Form(None),
#     condition: Optional[str] = Form(None),
#     main_category: Optional[str] = Form(None),
#     sub_category: Optional[str] = Form(None),
#     season: Optional[str] = Form(None),
#     size: Optional[str] = Form(None),
#     colors: Optional[str] = Form(None),  # JSON строка или список через запятую
#     tags: Optional[str] = Form(None),
#     brand: Optional[str] = Form(None),
#     # Изображения загружаются отдельно
#     images: Optional[list[UploadFile]] = File(None),
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user),
# ):
#     colors_list = []
#     if colors:
#         try:
#             # Пытаемся распарсить как JSON
#             import json
#             colors_list = json.loads(colors)
#         except:
#             # Или как список через запятую
#             colors_list = [c.strip() for c in colors.split(',') if c.strip()]

#     ad_data = AdCreate(
#         type=type,
#         title=title,
#         description=description,
#         price=price,
#         condition=condition,
#         main_category=main_category,
#         sub_category=sub_category,
#         season=season,
#         size=size,
#         colors=colors_list,
#         tags=tags,
#         brand=brand
#     )

#     print(f"📤 Создание объявления: {ad_data.title}")
#     print(f"📸 Загружено изображений: {len(images) if images else 0}")

#     """Создать новое объявление"""
#     ad = await AdService.create_ad(db, ad_data, current_user.id)
    
#     # Загружаем изображения, если они есть
#     if images:
#         for image in images:
#             await AdService.add_image_to_ad(
#                 db=db,
#                 ad_id=ad.id,
#                 image_file=image,  # Сервису нужно будет обработать UploadFile
#                 user_id=current_user.id,
#                 is_admin=current_user.is_admin
#             )
    
#     return ad

@router.post("/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
async def create_ad(
    ad_data: AdCreate,  # ← ВОЗВРАЩАЕМ JSON, а не Form
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Создать новое объявление"""
    
    print(f"📤 Создание объявления: {ad_data.title}")
    print(f"📤 Данные объявления: {ad_data.dict()}")
    
    ad = await AdService.create_ad(db, ad_data, current_user.id)
    
    return ad

@router.put("/{ad_id}", response_model=AdResponse)
async def update_ad_full(
    ad_id: int,
    ad_data: AdUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Полное обновление объявления (PUT)"""
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


@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(
    ad_id: int,
    soft_delete: bool = Query(True, description="Мягкое удаление (is_active=False)"),
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

@router.post("/{ad_id}/activate", response_model=AdResponse)
async def activate_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Активировать объявление"""
    update_data = AdUpdate(status=AdStatus.ACTIVE)
    ad = await AdService.update_ad(
        db=db,
        ad_id=ad_id,
        user_id=current_user.id,
        ad_data=update_data,
        is_admin=current_user.is_admin
    )
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено или нет прав доступа")
    return ad


@router.post("/{ad_id}/deactivate", response_model=AdResponse)
async def deactivate_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Деактивировать объявление"""
    update_data = AdUpdate(status=AdStatus.INACTIVE)
    ad = await AdService.update_ad(
        db=db,
        ad_id=ad_id,
        user_id=current_user.id,
        ad_data=update_data,
        is_admin=current_user.is_admin
    )
    if not ad:
        raise HTTPException(status_code=404, detail="Объявление не найдено или нет прав доступа")
    return ad


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
    """Загрузить изображение"""
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
