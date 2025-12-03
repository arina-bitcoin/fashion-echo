from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from sqlalchemy import select, update, delete, and_, or_, func, desc, asc, text, cast, String
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, Any
from datetime import datetime, timezone
import aiofiles
import aiofiles.os
from pathlib import Path
import re

from Backend.app.models.ad import Ad, FavoriteAd, AdImage
from Backend.app.models.user import User
from Backend.app.schemas.ad import (
    AdCreate, 
    AdUpdate, 
    AdSearch, 
    AdStatus,
    SortBy
)

class AdService:
    
    # ---------- Базовые CRUD операции ----------
    
    @staticmethod
    async def get_ads(
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        type: Optional[str] = None,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> list[Ad]:
        """Получить список объявлений с фильтрацией"""
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        )
        
        if active_only:
            stmt = stmt.where(Ad.is_active == True)
        
        if type:
            stmt = stmt.where(Ad.type == type)
        if category:
            stmt = stmt.where(Ad.category == category)
            
        stmt = stmt.offset(skip).limit(limit).order_by(desc(Ad.created_at))
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_ad(
        db: AsyncSession,
        ad_id: int
    ) -> Optional[Ad]:
        """Получить объявление по ID"""
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user),
            selectinload(Ad.favorited_by)
        ).where(Ad.id == ad_id)
        
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_ad(
        db: AsyncSession,
        ad_data: AdCreate,
        user_id: int
    ) -> Ad:
        """Создать новое объявление"""
        db_ad = Ad(**ad_data.model_dump(), user_id=user_id)
        db.add(db_ad)
        await db.commit()
        await db.refresh(db_ad, ['images', 'user'])
        return db_ad
    
    @staticmethod
    async def update_ad(
        db: AsyncSession, 
        ad_id: int, 
        user_id: int, 
        ad_data: AdUpdate, 
        is_admin: bool = False
    ) -> Optional[Ad]:
        """Обновить объявление"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return None
        
        # Обновляем только переданные поля
        update_data = ad_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:  # Позволяем сбрасывать значения в None если нужно
                setattr(ad, field, value)
        
        ad.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(ad, ['images', 'user'])
        return ad
    
    @staticmethod
    async def delete_ad(
        db: AsyncSession, 
        ad_id: int, 
        user_id: int, 
        is_admin: bool = False, 
        soft_delete: bool = True
    ) -> bool:
        """Удалить объявление (мягкое или физическое)"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return False
        
        if soft_delete:
            # Мягкое удаление
            ad.is_active = False
            ad.deleted_at = datetime.now(timezone.utc)
        else:
            # Физическое удаление
            # Сначала удаляем связанные записи
            await db.execute(
                delete(FavoriteAd).where(FavoriteAd.ad_id == ad_id)
            )
            await db.execute(
                delete(AdImage).where(AdImage.ad_id == ad_id)
            )
            # Затем само объявление
            await db.delete(ad)
        
        await db.commit()
        return True
    
    # ---------- Операции пользователя ----------
    
    @staticmethod
    async def get_user_ads(
        db: AsyncSession, 
        user_id: int, 
        active_only: Optional[bool] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> list[Ad]:
        """Получить объявления пользователя"""
        stmt = select(Ad).options(
            selectinload(Ad.images)
        ).where(Ad.user_id == user_id)
        
        if active_only is not None:
            stmt = stmt.where(Ad.is_active == active_only)
            
        stmt = stmt.offset(skip).limit(limit).order_by(desc(Ad.created_at))
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def toggle_ad_status(db: AsyncSession, ad_id: int, user_id: int, is_admin: bool = False, activate: bool = True) -> Optional[Ad]:
        """Активировать/деактивировать объявление"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return None
        
        ad.is_active = activate
        if not activate:
            ad.deactivated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(ad)
        return ad
    
    # ---------- Поиск ----------
    
    @staticmethod
    async def search_ads(
        db: AsyncSession,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        sort_by: str = "newest",  # newest, oldest, price_asc, price_desc, popular
        skip: int = 0,
        limit: int = 100
    ) -> list[Ad]:
        """Расширенный поиск объявлений"""
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        ).where(Ad.is_active == True)
        
        # Текстовый поиск
        if query:
            search_query = f"%{query}%"
            stmt = stmt.where(
                or_(
                    Ad.title.ilike(search_query),
                    Ad.description.ilike(search_query),
                    Ad.tags.ilike(search_query)
                )
            )
        
        # Фильтр по цене
        if min_price is not None:
            stmt = stmt.where(Ad.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Ad.price <= max_price)
        
        # Фильтр по типу
        if type:
            stmt = stmt.where(Ad.type == type)
        
        # Фильтр по категории
        if category:
            stmt = stmt.where(Ad.category == category)
        
        # Фильтр по местоположению
        if location:
            stmt = stmt.where(Ad.location.ilike(f"%{location}%"))
        
        # Сортировка
        if sort_by == "newest":
            stmt = stmt.order_by(desc(Ad.created_at))
        elif sort_by == "oldest":
            stmt = stmt.order_by(asc(Ad.created_at))
        elif sort_by == "price_asc":
            stmt = stmt.order_by(asc(Ad.price))
        elif sort_by == "price_desc":
            stmt = stmt.order_by(desc(Ad.price))
        elif sort_by == "popular":
            stmt = stmt.order_by(desc(Ad.view_count))
        
        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    

    @staticmethod
    async def advanced_search(
        db: AsyncSession,
        search_params: AdSearch
    ) -> dict[str, Any]:
        """
        Расширенный поиск объявлений с множественными фильтрами
        
        Возвращает:
        {
            "ads": List[Ad],          # Найденные объявления
            "total": int,             # Общее количество (без пагинации)
            "filters_applied": Dict   # Примененные фильтры
        }
        """
        # Базовый запрос
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        )

        applied_filters = {}

        # 1. ФИЛЬТРАЦИЯ ПО СТАТУСУ
        if search_params.status == AdStatus.ACTIVE:
            stmt = stmt.where(Ad.is_active == True)
            applied_filters["status"] = "active"
        elif search_params.status == AdStatus.INACTIVE:
            stmt = stmt.where(Ad.is_active == False)
            applied_filters["status"] = "inactive"
        # Для "all" не применяем фильтр
        
        # 2. ФИЛЬТРАЦИЯ ПО ТИПУ ОБЪЯВЛЕНИЯ
        if search_params.ad_type:
            stmt = stmt.where(Ad.type == search_params.ad_type)
            applied_filters["type"] = search_params.ad_type
        
        # 3. ФИЛЬТРАЦИЯ ПО ОСНОВНЫМ КАТЕГОРИЯМ (MULTI-SELECT)
        if search_params.main_categories:
            # Создаем условие OR для нескольких категорий
            category_conditions = []
            for category in search_params.main_categories:
                category_conditions.append(Ad.main_category == category)
            
            if category_conditions:
                stmt = stmt.where(or_(*category_conditions))
                applied_filters["main_categories"] = search_params.main_categories
        
        # 4. ФИЛЬТРАЦИЯ ПО ПОДКАТЕГОРИЯМ (MULTI-SELECT)
        if search_params.sub_categories:
            subcategory_conditions = []
            for subcategory in search_params.sub_categories:
                subcategory_conditions.append(Ad.sub_category == subcategory)
            
            if subcategory_conditions:
                stmt = stmt.where(or_(*subcategory_conditions))
                applied_filters["sub_categories"] = search_params.sub_categories
        
        # 5. ФИЛЬТРАЦИЯ ПО СЕЗОНАМ (MULTI-SELECT)
        if search_params.seasons:
            season_conditions = []
            for season in search_params.seasons:
                season_conditions.append(Ad.season == season)
            
            if season_conditions:
                stmt = stmt.where(or_(*season_conditions))
                applied_filters["seasons"] = search_params.seasons
        
        # 6. ФИЛЬТРАЦИЯ ПО ЦЕНОВОМУ ДИАПАЗОНУ
        price_filters = []
        
        if search_params.min_price is not None:
            price_filters.append(Ad.price >= search_params.min_price)
            applied_filters["min_price"] = search_params.min_price
        
        if search_params.max_price is not None:
            price_filters.append(Ad.price <= search_params.max_price)
            applied_filters["max_price"] = search_params.max_price
        
        if price_filters:
            stmt = stmt.where(and_(*price_filters))
        
        # 7. ФИЛЬТРАЦИЯ ПО СОСТОЯНИЮ ТОВАРА (MULTI-SELECT)
        if search_params.conditions:
            condition_filters = []
            for condition in search_params.conditions:
                condition_filters.append(Ad.condition == condition)
            
            if condition_filters:
                stmt = stmt.where(or_(*condition_filters))
                applied_filters["conditions"] = search_params.conditions
        
        # 8. ФИЛЬТРАЦИЯ ПО РАЗМЕРАМ (MULTI-SELECT + SMART MATCHING)
        if search_params.sizes:
            size_filters = []
            
            for size in search_params.sizes:
                size_lower = size.lower().strip()
                
                # Умное сопоставление размеров
                if size_lower in ["xs", "s", "m", "l", "xl", "xxl"]:
                    # Для буквенных размеров ищем точное совпадение
                    size_filters.append(
                        or_(
                            Ad.size.ilike(f"%{size_lower}%"),
                            Ad.size.ilike(f"%{size_lower.upper()}%")
                        )
                    )
                else:
                    # Для числовых размеров ищем частичное совпадение
                    size_filters.append(Ad.size.ilike(f"%{size_lower}%"))
            
            if size_filters:
                stmt = stmt.where(or_(*size_filters))
                applied_filters["sizes"] = search_params.sizes
        
        # 9. ФИЛЬТРАЦИЯ ПО ЦВЕТАМ (JSON ARRAY CONTAINS)
        if search_params.colors:
            # Для PostgreSQL используем оператор @>
            if db.bind.dialect.name == 'postgresql':
                # Преобразуем цвета в lowercase для поиска
                colors_lower = [color.lower() for color in search_params.colors]
                
                # Создаем условие для каждого цвета
                color_conditions = []
                for color in colors_lower:
                    # Ищем цвет в JSON массиве
                    color_conditions.append(
                        Ad.colors.op('@>')([color])
                    )
                
                if color_conditions:
                    stmt = stmt.where(or_(*color_conditions))
            else:
                # Для SQLite и других БД используем LIKE
                color_conditions = []
                for color in search_params.colors:
                    color_lower = color.lower()
                    color_conditions.append(
                        cast(Ad.colors, String).ilike(f'%"{color_lower}"%')
                    )
                
                if color_conditions:
                    stmt = stmt.where(or_(*color_conditions))
            
            applied_filters["colors"] = search_params.colors
        
        # 10. ТЕКСТОВЫЙ ПОИСК (ПОЛНОТЕКСТОВЫЙ ИЛИ LIKE)
        if search_params.query:
            query_clean = search_params.query.strip()
            
            # Разбиваем запрос на слова
            words = re.findall(r'\w+', query_clean.lower())
            
            if words:
                # Для PostgreSQL используем полнотекстовый поиск
                if db.bind.dialect.name == 'postgresql' and len(words) > 1:
                    # Создаем tsquery
                    ts_query = " & ".join(words)
                    stmt = stmt.where(
                        text(f"to_tsvector('russian', coalesce(title, '') || ' ' || "
                             f"coalesce(description, '') || ' ' || "
                             f"coalesce(tags, '')) @@ to_tsquery('russian', :ts_query)")
                    ).params(ts_query=ts_query)
                else:
                    # Для других БД используем LIKE по каждому слову
                    like_conditions = []
                    for word in words:
                        if len(word) > 2:  # Игнорируем слишком короткие слова
                            like_conditions.extend([
                                Ad.title.ilike(f"%{word}%"),
                                Ad.description.ilike(f"%{word}%"),
                                Ad.tags.ilike(f"%{word}%")
                            ])
                    
                    if like_conditions:
                        stmt = stmt.where(or_(*like_conditions))
            
            applied_filters["query"] = search_params.query
        
        # 11. ДОПОЛНИТЕЛЬНЫЕ ФИЛЬТРЫ
        
        # Фильтр по пользователю
        if search_params.user_id:
            stmt = stmt.where(Ad.user_id == search_params.user_id)
            applied_filters["user_id"] = search_params.user_id
        
        # Только с изображениями
        if search_params.has_images is True:
            stmt = stmt.where(Ad.images.any())  # Есть хотя бы одно изображение
            applied_filters["has_images"] = True
        
        # Возможен торг
        if search_params.is_negotiable is not None:
            stmt = stmt.where(Ad.is_negotiable == search_params.is_negotiable)
            applied_filters["is_negotiable"] = search_params.is_negotiable
        
        # 12. ПОДСЧЕТ ОБЩЕГО КОЛИЧЕСТВА (до пагинации)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # 13. СОРТИРОВКА
        if search_params.sort_by == SortBy.NEWEST:
            stmt = stmt.order_by(desc(Ad.created_at))
        elif search_params.sort_by == SortBy.OLDEST:
            stmt = stmt.order_by(asc(Ad.created_at))
        elif search_params.sort_by == SortBy.PRICE_ASC:
            stmt = stmt.order_by(asc(Ad.price))
        elif search_params.sort_by == SortBy.PRICE_DESC:
            stmt = stmt.order_by(desc(Ad.price))
        elif search_params.sort_by == SortBy.POPULAR:
            # Композитная сортировка: по просмотрам и избранным
            stmt = stmt.order_by(
                desc(Ad.view_count),
                desc(Ad.favorite_count),
                desc(Ad.created_at)
            )
        elif search_params.sort_by == SortBy.VIEWS:
            stmt = stmt.order_by(desc(Ad.view_count))
        elif search_params.sort_by == SortBy.FAVORITES:
            stmt = stmt.order_by(desc(Ad.favorite_count))
        
        applied_filters["sort_by"] = search_params.sort_by.value
        
        # 14. ПАГИНАЦИЯ
        stmt = stmt.offset(search_params.skip).limit(search_params.limit)
        applied_filters["pagination"] = {
            "skip": search_params.skip,
            "limit": search_params.limit,
            "total": total
        }
        
        # Выполняем запрос
        result = await db.execute(stmt)
        ads = result.scalars().all()
        
        return {
            "ads": ads,
            "total": total,
            "filters_applied": applied_filters,
            "has_more": (search_params.skip + search_params.limit) < total
        }
        
        # # Базовые условия
        # if search_data.only_active:
        #     stmt = stmt.where(Ad.is_active == True)
        
        # # 1. Текстовый поиск
        # if search_data.query:
        #     search_query = f"%{search_data.query}%"
        #     stmt = stmt.where(
        #         or_(
        #             Ad.title.ilike(search_query),
        #             Ad.description.ilike(search_query),
        #             Ad.tags.ilike(search_query),
        #             Ad.brand.ilike(search_query)
        #         )
        #     )
        
        # # 2. Фильтр по цене
        # if search_data.min_price is not None:
        #     stmt = stmt.where(Ad.price >= search_data.min_price)
        # if search_data.max_price is not None:
        #     stmt = stmt.where(Ad.price <= search_data.max_price)
        
        # # 3. Фильтр по типу объявления
        # if search_data.ad_types:
        #     type_conditions = []
        #     for ad_type in search_data.ad_types:
        #         type_conditions.append(Ad.type == ad_type.value)
        #     if type_conditions:
        #         stmt = stmt.where(or_(*type_conditions))
        
        # # 4. Фильтр по состоянию
        # if search_data.conditions:
        #     condition_filters = []
        #     for condition in search_data.conditions:
        #         condition_filters.append(Ad.condition == condition.value)
        #     if condition_filters:
        #         stmt = stmt.where(or_(*condition_filters))
        
        # # 5. Фильтр по размеру
        # if search_data.sizes:
        #     size_filters = []
        #     for size in search_data.sizes:
        #         size_filters.append(Ad.size.ilike(f"%{size}%"))
        #     if size_filters:
        #         stmt = stmt.where(or_(*size_filters))
        
        # # 6. Фильтр по бренду
        # if search_data.brands:
        #     brand_filters = []
        #     for brand in search_data.brands:
        #         brand_filters.append(Ad.brand.ilike(f"%{brand}%"))
        #     if brand_filters:
        #         stmt = stmt.where(or_(*brand_filters))
        
        # # 7. Фильтр по цвету
        # if search_data.colors:
        #     color_filters = []
        #     for color in search_data.colors:
        #         color_filters.append(Ad.color.ilike(f"%{color}%"))
        #     if color_filters:
        #         stmt = stmt.where(or_(*color_filters))
        
        # # 8. Фильтр по местоположению
        # if search_data.location:
        #     stmt = stmt.where(Ad.location.ilike(f"%{search_data.location}%"))
        
        # # 9. Фильтр по дате создания
        # if search_data.created_after:
        #     stmt = stmt.where(Ad.created_at >= search_data.created_after)
        # if search_data.created_before:
        #     stmt = stmt.where(Ad.created_at <= search_data.created_before)
        
        # # 10. Сложная фильтрация по категориям
        # if search_data.categories:
        #     category_conditions = search_data.categories.get_filter_conditions()
        #     if category_conditions:
        #         # Здесь нужно преобразовать строковые условия в SQLAlchemy
        #         # Это упрощенный пример, в реальности нужно использовать text() или другой подход
        #         for condition in category_conditions:
        #             # Для простоты предполагаем, что category хранится как строка с тегами
        #             # Например: "mens,casual,summer"
        #             pass
        
        # # 11. Только с изображениями
        # if search_data.only_with_images:
        #     stmt = stmt.where(Ad.images.any())
        
        # # 12. Только с возможностью торга
        # if search_data.only_negotiable is not None:
        #     stmt = stmt.where(Ad.is_negotiable == search_data.only_negotiable)
        
        # # 13. Только свежие
        # if search_data.only_fresh:
        #     from datetime import datetime, timedelta
        #     week_ago = datetime.utcnow() - timedelta(days=7)
        #     stmt = stmt.where(Ad.created_at >= week_ago)
        
        # # 14. ПРИМЕНЕНИЕ СОРТИРОВКИ
        # sort_expressions = search_data.get_sort_by()
        
        # # Преобразуем строковые выражения в SQLAlchemy order_by
        # for sort_expr in sort_expressions:
        #     if "created_at DESC" in sort_expr:
        #         stmt = stmt.order_by(desc(Ad.created_at))
        #     elif "created_at ASC" in sort_expr:
        #         stmt = stmt.order_by(asc(Ad.created_at))
        #     elif "price ASC" in sort_expr:
        #         stmt = stmt.order_by(asc(Ad.price))
        #     elif "price DESC" in sort_expr:
        #         stmt = stmt.order_by(desc(Ad.price))
        #     elif "popular" in sort_expr.lower():
        #         # Сложная сортировка по популярности
        #         stmt = stmt.order_by(
        #             desc((Ad.view_count * 0.5) + (Ad.favorite_count * 0.5))
        #         )
        #     elif "last_viewed" in sort_expr:
        #         stmt = stmt.order_by(desc(Ad.last_viewed))
        #     elif "updated_at" in sort_expr:
        #         stmt = stmt.order_by(desc(Ad.updated_at))
        #     elif "expires_at" in sort_expr:
        #         stmt = stmt.order_by(asc(Ad.expires_at))
        
        # # 15. ПАГИНАЦИЯ
        # stmt = stmt.offset(search_data.get_skip()).limit(search_data.get_limit())
        
        # # Выполняем запрос
        # result = await db.execute(stmt)
        # ads = result.scalars().all()
        
        # # Получаем общее количество для пагинации
        # count_stmt = select(func.count()).select_from(stmt.subquery())
        # total_result = await db.execute(count_stmt)
        # total_count = total_result.scalar()
        
        # return {
        #     "ads": ads,
        #     "total": total_count,
        #     "page": search_data.page,
        #     "per_page": search_data.per_page,
        #     "total_pages": (total_count + search_data.per_page - 1) // search_data.per_page
        # }
    
    @staticmethod
    async def get_filter_options(db: AsyncSession) -> dict[str, list[str]]:
        """
        Получить доступные опции для фильтров
        (для заполнения выпадающих списков на фронтенде)
        """
        # Основные категории
        main_categories_stmt = select(
            func.distinct(Ad.main_category)
        ).where(
            Ad.main_category.isnot(None),
            Ad.is_active == True
        ).order_by(Ad.main_category)
        
        # Подкатегории
        sub_categories_stmt = select(
            func.distinct(Ad.sub_category)
        ).where(
            Ad.sub_category.isnot(None),
            Ad.is_active == True
        ).order_by(Ad.sub_category)
        
        # Сезоны
        seasons_stmt = select(
            func.distinct(Ad.season)
        ).where(
            Ad.season.isnot(None),
            Ad.is_active == True
        ).order_by(Ad.season)
        
        # Состояния товара
        conditions_stmt = select(
            func.distinct(Ad.condition)
        ).where(
            Ad.condition.isnot(None),
            Ad.is_active == True
        ).order_by(Ad.condition)
        
        # Размеры (уникальные значения)
        sizes_stmt = select(
            func.distinct(Ad.size)
        ).where(
            Ad.size.isnot(None),
            Ad.size != '',
            Ad.is_active == True
        ).order_by(Ad.size)
        
        # Цвета (собираем из всех объявлений)
        colors_stmt = select(
            func.jsonb_array_elements_text(Ad.colors).label('color')
        ).where(
            Ad.colors.isnot(None),
            Ad.is_active == True
        ).distinct().order_by('color')
        
        # Выполняем все запросы параллельно
        results = await asyncio.gather(
            db.execute(main_categories_stmt),
            db.execute(sub_categories_stmt),
            db.execute(seasons_stmt),
            db.execute(conditions_stmt),
            db.execute(sizes_stmt),
            db.execute(colors_stmt)
        )
        
        # Обрабатываем результаты
        main_categories = [r[0] for r in results[0].all() if r[0]]
        sub_categories = [r[0] for r in results[1].all() if r[0]]
        seasons = [r[0] for r in results[2].all() if r[0]]
        conditions = [r[0] for r in results[3].all() if r[0]]
        sizes = [r[0] for r in results[4].all() if r[0]]
        colors = [r[0] for r in results[5].all() if r[0]]
        
        # Ценовые диапазоны
        price_stats_stmt = select(
            func.min(Ad.price).label('min_price'),
            func.max(Ad.price).label('max_price'),
            func.avg(Ad.price).label('avg_price')
        ).where(Ad.is_active == True)
        
        price_result = await db.execute(price_stats_stmt)
        price_stats = price_result.first()
        
        return {
            "main_categories": main_categories,
            "sub_categories": sub_categories,
            "seasons": seasons,
            "conditions": conditions,
            "sizes": sorted(set(sizes)),  # Удаляем дубликаты
            "colors": sorted(set(colors)),  # Удаляем дубликаты
            "price_range": {
                "min": float(price_stats.min_price) if price_stats.min_price else 0,
                "max": float(price_stats.max_price) if price_stats.max_price else 0,
                "avg": float(price_stats.avg_price) if price_stats.avg_price else 0
            }
        }

    @staticmethod
    async def get_sorted_ads(
        db: AsyncSession,
        sort_by: SortBy = SortBy.NEWEST,
        secondary_sort: Optional[SortBy] = None,
        **filters
    ) -> list[Ad]:
        """
        Упрощенный метод для сортировки с объяснением каждого параметра
        """
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        ).where(Ad.is_active == True)
        
        # Применяем фильтры
        for key, value in filters.items():
            if value is not None:
                if hasattr(Ad, key):
                    stmt = stmt.where(getattr(Ad, key) == value)
        
        # ----- ОСНОВНАЯ СОРТИРОВКА -----
        
        if sort_by == SortBy.NEWEST:
            """
            NEWEST - Самые новые объявления
            Сортировка по created_at DESC (по убыванию)
            Использование: Показывает свежие предложения первыми
            Подходит для: Главная страница, чтобы видеть актуальные объявления
            """
            stmt = stmt.order_by(desc(Ad.created_at))
            
        elif sort_by == SortBy.OLDEST:
            """
            OLDEST - Самые старые объявления
            Сортировка по created_at ASC (по возрастанию)
            Использование: Для модерации или анализа долго висящих объявлений
            """
            stmt = stmt.order_by(asc(Ad.created_at))
            
        elif sort_by == SortBy.PRICE_ASC:
            """
            PRICE_ASC - От дешевых к дорогим
            Сортировка по price ASC
            Использование: Для покупателей с ограниченным бюджетом
            Подходит для: Поиска бюджетных вариантов
            Особенность: Сначала показываются объявления без цены (если price=0)
            """
            stmt = stmt.order_by(asc(Ad.price))
            
        elif sort_by == SortBy.PRICE_DESC:
            """
            PRICE_DESC - От дорогих к дешевым
            Сортировка по price DESC
            Использование: Для поиска премиальных товаров
            Подходит для: Поиска брендовых вещей, антиквариата
            """
            stmt = stmt.order_by(desc(Ad.price))
            
        elif sort_by == SortBy.POPULAR:
            """
            POPULAR - Самые популярные
            Композитная сортировка по формуле: (просмотры * 0.5) + (избранное * 0.5)
            Использование: Показывает трендовые товары
            Подходит для: Рекомендаций, "хитов продаж"
            Особенность: Стимулирует активность (больше просмотров = выше в поиске)
            """
            # Пример формулы популярности
            popularity_score = (Ad.view_count * 0.5) + (Ad.favorite_count * 0.5)
            stmt = stmt.order_by(desc(popularity_score))
            
        elif sort_by == SortBy.RECENTLY_VIEWED:
            """
            RECENTLY_VIEWED - Недавно просмотренные
            Сортировка по last_viewed DESC
            Использование: Для возврата пользователей к просмотренным товарам
            Требует: Обновление поля last_viewed при каждом просмотре
            """
            stmt = stmt.order_by(desc(Ad.last_viewed))
            
        elif sort_by == SortBy.RECENTLY_UPDATED:
            """
            RECENTLY_UPDATED - Недавно обновленные
            Сортировка по updated_at DESC
            Использование: Показывает объявления, которые недавно редактировались
            Подходит для: Поиска актуальных предложений после изменения цены/описания
            """
            stmt = stmt.order_by(desc(Ad.updated_at))
            
        elif sort_by == SortBy.EXPIRING_SOON:
            """
            EXPIRING_SOON - Скоро истекают
            Сортировка по expires_at ASC
            Использование: Для срочных предложений, распродаж
            Требует: Поле expires_at с датой истечения
            """
            stmt = stmt.order_by(asc(Ad.expires_at))
            
        elif sort_by == SortBy.NEAREST:
            """
            NEAREST - Ближайшие по местоположению
            Сортировка по distance ASC
            Использование: Для локальных покупок, самовывоза
            Требует: Координаты объявления и пользователя
            Особенность: Нужно вычислять distance для каждого объявления
            """
            # Пример вычисления расстояния (нужны координаты)
            # distance = func.calculate_distance(Ad.lat, Ad.lng, user_lat, user_lng)
            # stmt = stmt.order_by(distance.asc())
            pass
        
        # ----- ВТОРИЧНАЯ СОРТИРОВКА -----
        # Применяется при равенстве значений основной сортировки
        
        if secondary_sort:
            if secondary_sort == SortBy.PRICE_ASC:
                stmt = stmt.order_by(asc(Ad.price))
            elif secondary_sort == SortBy.NEWEST:
                stmt = stmt.order_by(desc(Ad.created_at))
            # ... другие secondary сортировки
        
        # Выполняем запрос
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # ---------- Избранное ----------
    
    @staticmethod
    async def add_to_favorites(db: AsyncSession, ad_id: int, user_id: int) -> bool:
        """Добавить объявление в избранное"""
        # Проверяем, существует ли уже запись
        stmt = select(FavoriteAd).where(
            and_(FavoriteAd.ad_id == ad_id, FavoriteAd.user_id == user_id)
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            return False  # Уже в избранном
        
        # Проверяем, существует ли объявление
        ad = await AdService.get_ad(db, ad_id)
        if not ad:
            return False
        
        # Добавляем в избранное
        favorite = FavoriteAd(ad_id=ad_id, user_id=user_id)
        db.add(favorite)
        await db.commit()
        
        # Обновляем счетчик
        ad.favorite_count = (ad.favorite_count or 0) + 1
        await db.commit()
        
        return True
    
    @staticmethod
    async def remove_from_favorites(db: AsyncSession, ad_id: int, user_id: int) -> bool:
        """Удалить объявление из избранного"""
        stmt = select(FavoriteAd).where(
            and_(FavoriteAd.ad_id == ad_id, FavoriteAd.user_id == user_id)
        )
        result = await db.execute(stmt)
        favorite = result.scalar_one_or_none()
        
        if not favorite:
            return False
        
        await db.delete(favorite)
        await db.commit()
        
        # Обновляем счетчик
        ad = await AdService.get_ad(db, ad_id)
        if ad and ad.favorite_count > 0:
            ad.favorite_count -= 1
            await db.commit()
        
        return True
    
    @staticmethod
    async def get_favorite_ads(db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100) -> list[Ad]:
        """Получить избранные объявления пользователя"""
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        ).join(
            FavoriteAd, Ad.id == FavoriteAd.ad_id
        ).where(
            FavoriteAd.user_id == user_id,
            Ad.is_active == True
        ).offset(skip).limit(limit).order_by(desc(FavoriteAd.created_at))
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def is_favorite(db: AsyncSession, ad_id: int, user_id: int) -> bool:
        """Проверить, есть ли объявление в избранном у пользователя"""
        stmt = select(FavoriteAd).where(
            and_(FavoriteAd.ad_id == ad_id, FavoriteAd.user_id == user_id)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    # ---------- Управление изображениями ----------
    
    @staticmethod
    async def add_image_to_ad(db: AsyncSession, ad_id: int, image_path: str, user_id: int, is_admin: bool = False) -> Optional[AdImage]:
        """Добавить изображение к объявлению"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return None
        
        # Создаем запись изображения
        image = AdImage(ad_id=ad_id, file_path=image_path)
        db.add(image)
        await db.commit()
        await db.refresh(image)
        return image
    
    @staticmethod
    async def add_multiple_images(db: AsyncSession, ad_id: int, image_paths: list[str], user_id: int, is_admin: bool = False) -> list[AdImage]:
        """Добавить несколько изображений к объявлению"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return []
        
        images = []
        for path in image_paths:
            image = AdImage(ad_id=ad_id, file_path=path)
            db.add(image)
            images.append(image)
        
        await db.commit()
        
        # Обновляем изображения
        for image in images:
            await db.refresh(image)
        
        return images
    
    @staticmethod
    async def delete_image(db: AsyncSession, filename: str, user_id: int, is_admin: bool = False) -> bool:
        """Удалить изображение"""
        # Находим изображение
        stmt = select(AdImage).options(
            selectinload(AdImage.ad)
        ).where(AdImage.file_path.ilike(f"%{filename}"))
        
        result = await db.execute(stmt)
        image = result.scalar_one_or_none()
        
        if not image or not image.ad:
            return False
        
        # Проверяем права доступа
        if not is_admin and image.ad.user_id != user_id:
            return False
        
        # Удаляем файл с диска
        file_path = Path(image.file_path)
        if file_path.exists():
            await aiofiles.os.remove(file_path)
        
        # Удаляем запись из БД
        await db.delete(image)
        await db.commit()
        return True
    
    @staticmethod
    async def update_image_order(db: AsyncSession, ad_id: int, image_ids: list[int], user_id: int, is_admin: bool = False) -> bool:
        """Обновить порядок изображений"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return False
        
        # Обновляем порядок для каждого изображения
        for order, image_id in enumerate(image_ids, 1):
            await db.execute(
                update(AdImage)
                .where(and_(AdImage.id == image_id, AdImage.ad_id == ad_id))
                .values(order=order)
            )
        
        await db.commit()
        return True
    
    @staticmethod
    async def get_ad_images(db: AsyncSession, ad_id: int) -> list[AdImage]:
        """Получить изображения объявления"""
        stmt = select(AdImage).where(
            AdImage.ad_id == ad_id
        ).order_by(AdImage.order)
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    # ---------- Статистика ----------
    
    @staticmethod
    async def increment_view_count(db: AsyncSession, ad_id: int) -> None:
        """Увеличить счетчик просмотров"""
        await db.execute(
            update(Ad)
            .where(Ad.id == ad_id)
            .values(view_count=Ad.view_count + 1)
        )
        await db.commit()
    
    @staticmethod
    async def get_ad_stats(db: AsyncSession, ad_id: int, user_id: int, is_admin: bool = False) -> Optional[dict[str, Any]]:
        """Получить статистику объявления"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).where(and_(Ad.id == ad_id, Ad.user_id == user_id))
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return None
        
        return {
            "views": ad.view_count or 0,
            "favorites": ad.favorite_count or 0,
            "created_at": ad.created_at,
            "updated_at": ad.updated_at,
            "is_active": ad.is_active
        }