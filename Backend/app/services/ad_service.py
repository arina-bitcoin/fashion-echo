from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func, cast, String
from typing import Optional, List
from Backend.app.models.ad import Ad
from Backend.app.schemas.ad import AdCreate
import json

class AdService:
    @staticmethod
    async def get_ads(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,  # all, active, inactive
        type: Optional[str] = None,  # sell, exchange, buy_request
        main_categories: Optional[List[str]] = None,
        subcategories: Optional[List[str]] = None,
        seasons: Optional[List[str]] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        condition: Optional[List[str]] = None,
        sizes: Optional[List[str]] = None,
        colors: Optional[List[str]] = None,
        search: Optional[str] = None,  # Текстовый поиск
        sort: Optional[str] = None  # newest, oldest, price_asc, price_desc, popular
    ) -> list[Ad]:
        # Создаем базовый запрос
        if status == "active" or status is None:
            stmt = select(Ad).filter(Ad.is_active == True)
        elif status == "inactive":
            stmt = select(Ad).filter(Ad.is_active == False)
        else:  # status == "all"
            stmt = select(Ad)
        
        # Фильтр по типу
        if type:
            stmt = stmt.filter(Ad.type == type)
        
        # Фильтр по основным категориям (хотя бы одна должна совпадать)
        # Используем LIKE для SQLite (JSON хранится как текст)
        if main_categories and len(main_categories) > 0:
            conditions = []
            for cat in main_categories:
                if cat:  # Проверяем, что категория не пустая
                    # Ищем категорию в JSON массиве (как строку)
                    conditions.append(
                        (Ad.main_categories.isnot(None)) & 
                        (cast(Ad.main_categories, String).like(f'%"{cat}"%'))
                    )
                    conditions.append(
                        (Ad.main_categories.isnot(None)) & 
                        (cast(Ad.main_categories, String).like(f'%{cat}%'))
                    )
            if conditions:
                stmt = stmt.filter(or_(*conditions))
        
        # Фильтр по подкатегориям (хотя бы одна должна совпадать)
        if subcategories and len(subcategories) > 0:
            conditions = []
            for subcat in subcategories:
                if subcat:
                    conditions.append(
                        (Ad.subcategories.isnot(None)) & 
                        (cast(Ad.subcategories, String).like(f'%"{subcat}"%'))
                    )
                    conditions.append(
                        (Ad.subcategories.isnot(None)) & 
                        (cast(Ad.subcategories, String).like(f'%{subcat}%'))
                    )
            if conditions:
                stmt = stmt.filter(or_(*conditions))
        
        # Фильтр по сезонам (хотя бы один должен совпадать)
        if seasons and len(seasons) > 0:
            conditions = []
            for season in seasons:
                if season:
                    conditions.append(
                        (Ad.seasons.isnot(None)) & 
                        (cast(Ad.seasons, String).like(f'%"{season}"%'))
                    )
                    conditions.append(
                        (Ad.seasons.isnot(None)) & 
                        (cast(Ad.seasons, String).like(f'%{season}%'))
                    )
            if conditions:
                stmt = stmt.filter(or_(*conditions))
        
        # Фильтр по цене
        if min_price is not None:
            stmt = stmt.filter(Ad.price >= min_price)
        if max_price is not None:
            stmt = stmt.filter(Ad.price <= max_price)
        
        # Фильтр по состоянию
        if condition:
            stmt = stmt.filter(Ad.condition.in_(condition))
        
        # Фильтр по размерам (частичное совпадение)
        if sizes:
            size_conditions = []
            for size in sizes:
                size_conditions.append(Ad.size.ilike(f"%{size}%"))
            stmt = stmt.filter(or_(*size_conditions))
        
        # Фильтр по цветам (хотя бы один должен совпадать)
        if colors and len(colors) > 0:
            color_conditions = []
            for color in colors:
                if color:
                    color_conditions.append(
                        (Ad.colors.isnot(None)) & 
                        (cast(Ad.colors, String).like(f'%"{color}"%'))
                    )
                    color_conditions.append(
                        (Ad.colors.isnot(None)) & 
                        (cast(Ad.colors, String).like(f'%{color}%'))
                    )
            if color_conditions:
                stmt = stmt.filter(or_(*color_conditions))
        
        # Текстовый поиск (по заголовку и описанию)
        if search:
            search_filter = or_(
                Ad.title.ilike(f"%{search}%"),
                Ad.description.ilike(f"%{search}%"),
                Ad.brand.ilike(f"%{search}%")
            )
            stmt = stmt.filter(search_filter)
        
        # Сортировка
        if sort == "newest" or sort is None:
            stmt = stmt.order_by(Ad.created_at.desc())
        elif sort == "oldest":
            stmt = stmt.order_by(Ad.created_at.asc())
        elif sort == "price_asc":
            stmt = stmt.order_by(Ad.price.asc().nulls_last())
        elif sort == "price_desc":
            stmt = stmt.order_by(Ad.price.desc().nulls_last())
        elif sort == "popular":
            # Для популярности можно использовать количество просмотров (если добавить поле) или просто по дате
            stmt = stmt.order_by(Ad.created_at.desc())
        
        # Применяем пагинацию
        stmt = stmt.offset(skip).limit(limit)
        
        # Выполняем запрос
        result = await db.execute(stmt)
        return list(result.scalars().all())
    
    @staticmethod
    async def create_ad(db: AsyncSession, ad_data: AdCreate, user_id: int) -> Ad:
        ad_dict = ad_data.dict()
        
        # Убираем дубликаты из списка изображений, если они есть
        if 'images' in ad_dict and ad_dict['images']:
            # Фильтруем None и пустые строки, убираем дубликаты
            images_list = [img for img in ad_dict['images'] if img and isinstance(img, str) and img.strip()]
            ad_dict['images'] = list(dict.fromkeys(images_list))  # Сохраняет порядок и убирает дубликаты
            print(f"🔍 Обработанные изображения: {ad_dict['images']}")
        else:
            ad_dict['images'] = []
        
        db_ad = Ad(**ad_dict, user_id=user_id)
        db.add(db_ad)
        await db.commit()
        await db.refresh(db_ad)
        return db_ad
    
    @staticmethod
    async def get_ad(db: AsyncSession, ad_id: int) -> Optional[Ad]:
        """Получить объявление по ID"""
        stmt = select(Ad).filter(Ad.id == ad_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_ads(db: AsyncSession, user_id: int) -> List[Ad]:
        stmt = select(Ad).filter(Ad.user_id == user_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())
