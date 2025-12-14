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
        status: Optional[str] = None,
        type: Optional[str] = None,
        main_category: Optional[str] = None,
        sub_category: Optional[str] = None,
        season: Optional[str] = None,
        condition: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        size: Optional[str] = None,
        color: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[str] = "newest"
    ) -> list[Ad]:
        print(f"🎯 DEBUG get_ads called with search='{search}'")
        """Получить список объявлений с фильтрацией"""
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        )
        
        # Фильтр по статусу (активные по умолчанию)
        if status:
            if status.lower() == "active":
                stmt = stmt.where(Ad.status == AdStatus.ACTIVE)
            elif status.lower() == "inactive":
                stmt = stmt.where(Ad.status == AdStatus.INACTIVE)
        else:
            # По умолчанию показываем только активные
            stmt = stmt.where(Ad.status == AdStatus.ACTIVE)
        
        # Фильтр по типу
        if type:
            stmt = stmt.where(Ad.type == type)

        # Фильтр по основной категории
        if main_category and hasattr(Ad, 'main_category'):
            # print(f"🔍 DEBUG: Filtering by main_category='{main_category}' (type: {type(main_category).__name__})")
            
            # Если main_category - это список
            if isinstance(main_category, list) and len(main_category) > 0:
                # print(f"🔍 DEBUG: Filtering by categories list: {main_category}")
                if len(main_category) == 1:
                    stmt = stmt.where(Ad.main_category == main_category[0])
                else:
                    stmt = stmt.where(Ad.main_category.in_(main_category))
            elif isinstance(main_category, str) and main_category.strip():
                # Если строка
                stmt = stmt.where(Ad.main_category == main_category.strip())

        # Фильтр по подкатегории
        if sub_category and hasattr(Ad, 'sub_category'):
            stmt = stmt.where(Ad.sub_category == sub_category)
        
        # Фильтр по сезону
        if season and hasattr(Ad, 'season'):
            stmt = stmt.where(Ad.season == season)
        
        # Фильтр по состоянию
        if condition and hasattr(Ad, 'condition'):
            stmt = stmt.where(Ad.condition == condition)

        # Фильтр по цене
        if min_price is not None:
            stmt = stmt.where(Ad.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Ad.price <= max_price)

        # Фильтр по размеру
        if size and hasattr(Ad, 'size'):
            stmt = stmt.where(Ad.size.ilike(f"%{size}%"))
        
        # Фильтр по цвету
        if color and hasattr(Ad, 'colors'):
            try:
                # Для PostgreSQL
                if db.bind.dialect.name == 'postgresql':
                    stmt = stmt.where(
                        Ad.colors.op('@>')([color.lower()])
                    )
                else:
                    stmt = stmt.where(
                        cast(Ad.colors, String).ilike(f'%"{color.lower()}"%')
                    )
            except:
                pass  # Игнорируем ошибки если поле colors не существует
        
        # Текстовый поиск
        if search:
            search_lower = search.lower()
            print(f"🔍 DEBUG: Search lower (Python): '{search_lower}'")
            
            # Получаем ВСЕ активные объявления
            all_ads_stmt = select(Ad).where(Ad.status == AdStatus.ACTIVE)
            all_ads_result = await db.execute(all_ads_stmt)
            all_active_ads = all_ads_result.scalars().all()
            
            # Фильтруем в Python
            filtered_ads_ids = []
            for ad in all_active_ads:
                # Приводим всё к нижнему регистру в Python
                title_lower = ad.title.lower() if ad.title else ""
                description_lower = ad.description.lower() if ad.description else ""
                tags_lower = ad.tags.lower() if ad.tags else ""
                
                if (search_lower in title_lower or 
                    search_lower in description_lower or 
                    search_lower in tags_lower):
                    filtered_ads_ids.append(ad.id)
            
            print(f"🔍 DEBUG: Found {len(filtered_ads_ids)} ads after Python filtering: {filtered_ads_ids}")
            
            # Если найдены объявления, фильтруем по ID
            if filtered_ads_ids:
                stmt = stmt.where(Ad.id.in_(filtered_ads_ids))
            else:
                # Если ничего не найдено, возвращаем пустой результат
                stmt = stmt.where(False)  # Всегда false
        
        # Сортировка
        if sort == "newest":
            stmt = stmt.order_by(desc(Ad.created_at))
        elif sort == "oldest":
            stmt = stmt.order_by(asc(Ad.created_at))
        elif sort == "price_asc":
            stmt = stmt.order_by(asc(Ad.price))
        elif sort == "price_desc":
            stmt = stmt.order_by(desc(Ad.price))
        elif sort == "popular":
            # Композитная сортировка по просмотрам и избранным
            stmt = stmt.order_by(
                desc(Ad.view_count),
                desc(Ad.favorite_count),
                desc(Ad.created_at)
            )
        else:
            stmt = stmt.order_by(desc(Ad.created_at))
        
        # Пагинация
        stmt = stmt.offset(skip).limit(limit)
        
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
            selectinload(Ad.favorited_by_users)
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

        # Преобразуем данные в словарь
        ad_dict = ad_data.model_dump()
        
        # Исправляем пустой список colors для JSON поля
        if 'colors' in ad_dict and ad_dict['colors'] == []:
            ad_dict['colors'] = []  # Оставляем как пустой список, но нужно убедиться, что он правильно сериализуется

        db_ad = Ad(**ad_data.model_dump(), user_id=user_id, status=AdStatus.ACTIVE)
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
        """Обновить объявление с обработкой изображений"""
        # Проверяем права доступа
        if is_admin:
            stmt = select(Ad).options(selectinload(Ad.images)).where(Ad.id == ad_id)
        else:
            stmt = select(Ad).options(selectinload(Ad.images)).where(
                and_(Ad.id == ad_id, Ad.user_id == user_id)
            )
        
        result = await db.execute(stmt)
        ad = result.scalar_one_or_none()
        
        if not ad:
            return None
        
        # Извлекаем данные об изображениях
        update_dict = ad_data.model_dump(exclude_unset=True)
        # Проверяем, было ли поле images передано явно
        if 'images' in update_dict:
            new_image_paths = update_dict.pop('images')  # Убираем images из общего обновления
        else:
            new_image_paths = None  # Поле не было передано - не обновляем изображения
        
        # Обновляем основные поля
        for field, value in update_dict.items():
            if value is not None:
                setattr(ad, field, value)
        
        ad.updated_at = datetime.now(timezone.utc)
        
        # Обработка изображений, если переданы новые
        # None означает "не обновлять изображения", список с путями - "обновить список изображений"
        if new_image_paths is not None and isinstance(new_image_paths, list):
            # Получаем текущие пути к изображениям
            current_paths = {img.file_path for img in ad.images}
            new_paths_set = {path for path in new_image_paths if path and isinstance(path, str)}
            
            # Удаляем изображения, которых нет в новом списке
            images_to_delete = []
            for old_image in ad.images:
                if old_image.file_path not in new_paths_set:
                    images_to_delete.append(old_image)
                    # Удаляем файл с диска только если это не системный путь
                    file_path = Path(old_image.file_path)
                    if file_path.exists() and not str(file_path).startswith('media/'):
                        try:
                            await aiofiles.os.remove(file_path)
                        except Exception as e:
                            print(f"Error removing old image {file_path}: {e}")
            
            # Удаляем записи из БД для удаленных изображений
            if images_to_delete:
                delete_ids = [img.id for img in images_to_delete]
                await db.execute(
                    delete(AdImage).where(AdImage.id.in_(delete_ids))
                )
            
            # Добавляем новые изображения (которых еще нет в БД)
            for order, image_path in enumerate(new_image_paths):
                if image_path and isinstance(image_path, str):
                    # Проверяем, не существует ли уже такое изображение
                    existing_image = next((img for img in ad.images if img.file_path == image_path), None)
                    if not existing_image:
                        # Извлекаем имя файла из пути
                        filename = Path(image_path).name
                        image = AdImage(
                            ad_id=ad_id,
                            file_path=image_path,
                            filename=filename,
                            order=order,
                            is_main=(order == 0)  # Первое изображение - главное
                        )
                        db.add(image)
            
            # Обновляем порядок и главное изображение для всех существующих изображений
            for order, image_path in enumerate(new_image_paths):
                if image_path and isinstance(image_path, str):
                    existing_image = next((img for img in ad.images if img.file_path == image_path), None)
                    if existing_image:
                        existing_image.order = order
                        existing_image.is_main = (order == 0)

        update_data = ad_data.model_dump(exclude_unset=True)
    
        # Исправляем colors, если передается None или пустой список
        if 'colors' in update_data:
            if update_data['colors'] is None:
                update_data['colors'] = []
        
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
        soft_delete: bool = False
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
            ad.status = AdStatus.INACTIVE
            # ad.deleted_at = datetime.now(timezone.utc)
        else:
            # Физическое удаление
            # Сначала удаляем связанные записи
            await db.execute(
                delete(FavoriteAd).where(FavoriteAd.ad_id == ad_id)
            )
            
            # Удаляем изображения с диска
            images_stmt = select(AdImage).where(AdImage.ad_id == ad_id)
            images_result = await db.execute(images_stmt)
            images = images_result.scalars().all()
            
            for image in images:
                file_path = Path(image.file_path)
                if file_path.exists():
                    try:
                        await aiofiles.os.remove(file_path)
                    except:
                        pass  # Игнорируем ошибки удаления файла
            
            # Удаляем записи изображений
            await db.execute(
                delete(AdImage).where(AdImage.ad_id == ad_id)
            )
            
            # Удаляем само объявление
            await db.delete(ad)
            await db.commit()
            return True
    
    # ---------- Операции пользователя ----------
    
    @staticmethod
    async def get_user_ads(
        db: AsyncSession, 
        user_id: int, 
        status: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> list[dict[str, Any]]:
        """Получить объявления пользователя"""
        
        stmt = select(Ad).options(
            selectinload(Ad.images)
        ).where(Ad.user_id == user_id)
        
        if status is not None:
            if status == "active":
                stmt = stmt.where(Ad.status == AdStatus.ACTIVE)
            elif status == "inactive":
                stmt = stmt.where(Ad.status == AdStatus.INACTIVE)
            # Можно добавить другие статусы при необходимости
            
        stmt = stmt.offset(skip).limit(limit).order_by(desc(Ad.created_at))
        
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def toggle_ad_status(
        db: AsyncSession, 
        ad_id: int, 
        user_id: int, 
        is_admin: bool = False, 
        activate: bool = True
    ) -> Optional[Ad]:
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
        
        if activate:
            ad.status = AdStatus.ACTIVE
        else:
            ad.status = AdStatus.INACTIVE
            # ad.deactivated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(ad)
        return ad
    
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
            Ad.status == AdStatus.ACTIVE
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
        
        # Извлекаем имя файла из пути
        filename = Path(image_path).name
        
        # Создаем запись изображения
        image = AdImage(ad_id=ad_id, file_path=image_path, filename=filename)
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
            # Извлекаем имя файла из пути
            filename = Path(path).name
            image = AdImage(ad_id=ad_id, file_path=path, filename=filename)
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
    async def get_ad_stats(
        db: AsyncSession, 
        ad_id: int, 
        user_id: int, 
        is_admin: bool = False
    ) -> Optional[dict[str, Any]]:
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
            "status": ad.status if ad.status else "unknown"
        }
    
    # ---------- Поиск и фильтрация ----------
    
    @staticmethod
    async def advanced_search(db: AsyncSession, search_data: AdSearch) -> dict[str, Any]:
        """Расширенный поиск объявлений с использованием AdSearch схемы"""
        stmt = select(Ad).options(
            selectinload(Ad.images),
            selectinload(Ad.user)
        )
        
        # Фильтр по статусу
        if search_data.status and search_data.status != AdStatus.ALL:
            stmt = stmt.where(Ad.status == search_data.status)
        elif not search_data.status or search_data.status == AdStatus.ALL:
            # По умолчанию показываем только активные
            stmt = stmt.where(Ad.status == AdStatus.ACTIVE)
        
        # Фильтр по типу объявления
        if search_data.ad_type:
            stmt = stmt.where(Ad.type == search_data.ad_type)
        
        # Фильтр по основным категориям
        if search_data.main_categories:
            stmt = stmt.where(Ad.main_category.in_(search_data.main_categories))
        
        # Фильтр по подкатегориям
        if search_data.sub_categories:
            stmt = stmt.where(Ad.sub_category.in_(search_data.sub_categories))
        
        # Фильтр по сезонам
        if search_data.seasons:
            stmt = stmt.where(Ad.season.in_(search_data.seasons))
        
        # Фильтр по состоянию товара
        if search_data.conditions:
            stmt = stmt.where(Ad.condition.in_(search_data.conditions))
        
        # Фильтр по размерам
        if search_data.sizes:
            size_conditions = [Ad.size.ilike(f"%{size}%") for size in search_data.sizes]
            stmt = stmt.where(or_(*size_conditions))
        
        # Фильтр по цветам
        if search_data.colors:
            color_conditions = []
            for color in search_data.colors:
                color_conditions.append(cast(Ad.colors, String).ilike(f'%"{color.lower()}"%'))
            if color_conditions:
                stmt = stmt.where(or_(*color_conditions))
        
        # Ценовой диапазон
        if search_data.min_price is not None:
            stmt = stmt.where(Ad.price >= search_data.min_price)
        if search_data.max_price is not None:
            stmt = stmt.where(Ad.price <= search_data.max_price)
        
        # Текстовый поиск
        if search_data.query:
            query_lower = search_data.query.lower()
            stmt = stmt.where(
                or_(
                    Ad.title.ilike(f"%{query_lower}%"),
                    Ad.description.ilike(f"%{query_lower}%"),
                    Ad.tags.ilike(f"%{query_lower}%")
                )
            )
        
        # Дополнительные фильтры
        if search_data.user_id:
            stmt = stmt.where(Ad.user_id == search_data.user_id)
        
        if search_data.has_images is not None:
            if search_data.has_images:
                stmt = stmt.where(Ad.images.any())
        
        # Сортировка
        sort_by = search_data.sort_by or SortBy.NEWEST
        if sort_by == SortBy.NEWEST:
            stmt = stmt.order_by(desc(Ad.created_at))
        elif sort_by == SortBy.OLDEST:
            stmt = stmt.order_by(asc(Ad.created_at))
        elif sort_by == SortBy.PRICE_ASC:
            stmt = stmt.order_by(asc(Ad.price))
        elif sort_by == SortBy.PRICE_DESC:
            stmt = stmt.order_by(desc(Ad.price))
        elif sort_by == SortBy.POPULAR:
            stmt = stmt.order_by(desc(Ad.view_count + Ad.favorite_count))
        
        # Подсчет общего количества (до пагинации)
        count_stmt = select(func.count(Ad.id)).select_from(stmt.subquery())
        total_result = await db.execute(count_stmt)
        total = total_result.scalar() or 0
        
        # Пагинация
        skip = search_data.skip or 0
        limit = search_data.limit or 50
        stmt = stmt.offset(skip).limit(limit)
        
        # Выполняем запрос
        result = await db.execute(stmt)
        ads = result.scalars().all()
        
        return {
            "ads": ads,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    async def search_ads(
        db: AsyncSession,
        query: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        type: Optional[str] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        sort_by: Optional[str] = "newest",
        skip: int = 0,
        limit: int = 100
    ) -> list[Ad]:
        """Простой поиск объявлений (для обратной совместимости)"""
        return await AdService.get_ads(
            db=db,
            skip=skip,
            limit=limit,
            search=query,
            min_price=min_price,
            max_price=max_price,
            type=type,
            main_category=category,
            sort=sort_by
        )
    
    @staticmethod
    async def get_filter_options(db: AsyncSession) -> dict[str, Any]:
        """Получить все доступные опции для фильтров"""
        # Основные категории
        main_categories_stmt = select(func.distinct(Ad.main_category)).where(
            Ad.main_category.isnot(None),
            Ad.status == AdStatus.ACTIVE
        )
        main_categories_result = await db.execute(main_categories_stmt)
        main_categories = [row[0] for row in main_categories_result.all() if row[0]]
        
        # Подкатегории
        sub_categories_stmt = select(func.distinct(Ad.sub_category)).where(
            Ad.sub_category.isnot(None),
            Ad.status == AdStatus.ACTIVE
        )
        sub_categories_result = await db.execute(sub_categories_stmt)
        sub_categories = [row[0] for row in sub_categories_result.all() if row[0]]
        
        # Сезоны
        seasons_stmt = select(func.distinct(Ad.season)).where(
            Ad.season.isnot(None),
            Ad.status == AdStatus.ACTIVE
        )
        seasons_result = await db.execute(seasons_stmt)
        seasons = [row[0] for row in seasons_result.all() if row[0]]
        
        # Состояния
        conditions_stmt = select(func.distinct(Ad.condition)).where(
            Ad.condition.isnot(None),
            Ad.status == AdStatus.ACTIVE
        )
        conditions_result = await db.execute(conditions_stmt)
        conditions = [row[0] for row in conditions_result.all() if row[0]]
        
        # Размеры
        sizes_stmt = select(func.distinct(Ad.size)).where(
            Ad.size.isnot(None),
            Ad.size != '',
            Ad.status == AdStatus.ACTIVE
        )
        sizes_result = await db.execute(sizes_stmt)
        sizes = [row[0] for row in sizes_result.all() if row[0]]
        
        # Цвета (извлекаем из JSON)
        colors_stmt = select(Ad.colors).where(
            Ad.colors.isnot(None),
            Ad.status == AdStatus.ACTIVE
        )
        colors_result = await db.execute(colors_stmt)
        all_colors = set()
        for row in colors_result.all():
            if row[0] and isinstance(row[0], list):
                all_colors.update(row[0])
        colors = sorted(list(all_colors))
        
        return {
            "main_categories": main_categories,
            "sub_categories": sub_categories,
            "seasons": seasons,
            "conditions": conditions,
            "sizes": sizes,
            "colors": colors
        }