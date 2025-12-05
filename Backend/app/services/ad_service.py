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
        new_image_paths = update_dict.pop('images', None)  # Убираем images из общего обновления
        
        # Обновляем основные поля
        for field, value in update_dict.items():
            if value is not None:
                setattr(ad, field, value)
        
        ad.updated_at = datetime.now(timezone.utc)
        
        # Обработка изображений, если переданы новые
        if new_image_paths is not None:
            # Удаляем старые изображения (опционально)
            for old_image in ad.images:
                # Удаляем файлы с диска
                file_path = Path(old_image.file_path)
                if file_path.exists():
                    try:
                        await aiofiles.os.remove(file_path)
                    except Exception as e:
                        print(f"Error removing old image {file_path}: {e}")
            
            # Удаляем записи из БД
            await db.execute(
                delete(AdImage).where(AdImage.ad_id == ad_id)
            )
            
            # Добавляем новые изображения
            for order, image_path in enumerate(new_image_paths):
                if image_path and isinstance(image_path, str):
                    image = AdImage(
                        ad_id=ad_id,
                        file_path=image_path,
                        order=order,
                        is_main=(order == 0)  # Первое изображение - главное
                    )
                    db.add(image)

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
