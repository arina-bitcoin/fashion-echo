from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, select
from typing import List, Optional, Tuple
import logging
import math

from Backend.app.models.secondhand import Secondhand
from Backend.app.schemas.secondhand import (
    SecondhandCreate,
    SecondhandUpdate,
    SecondhandFilters,
    MapClusterResponse,
)
from Backend.app.core.cache import cache
from Backend.app.services.map_service import MapService

logger = logging.getLogger(__name__)
SECONDHAND_CITY_CACHE_PREFIX = "secondhands:city:"


class SecondhandService:
    def __init__(self):
        self.map_service = MapService()

    async def get_secondhand_by_id(self, db: AsyncSession, secondhand_id: int) -> Optional[Secondhand]:
        """
        Получить секондхенд по ID
        """
        try:
            stmt = select(Secondhand).filter(
                Secondhand.id == secondhand_id,
                Secondhand.is_active == True
            )
            result = await db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting secondhand by id {secondhand_id}: {e}")
            return None

    async def get_secondhands(
        self, 
        db: AsyncSession, 
        filters: SecondhandFilters,
        skip: int = 0,
        limit: int = 100,
    ) -> Tuple[List[Secondhand], int]:
        try:
            stmt = select(Secondhand)
            
            # Применяем фильтры
            stmt = self._apply_filters(stmt, filters)
            
            # Получаем общее количество для пагинации
            count_stmt = select(func.count()).select_from(stmt.subquery())
            count_result = await db.execute(count_stmt)
            total = count_result.scalar() or 0
            
            # Применяем пагинацию и сортировку
            stmt = stmt.order_by(Secondhand.name.asc()).offset(skip).limit(limit)
            result = await db.execute(stmt)
            items = result.scalars().all()
            
            return list(items), total
            
        except Exception as e:
            logger.error(f"Error getting secondhands: {e}")
            return [], 0

    def _apply_filters(self, stmt, filters: SecondhandFilters):
        """
        Применить фильтры к запросу
        """
        # Фильтр по активности
        if filters.is_active is not None:
            stmt = stmt.filter(Secondhand.is_active == filters.is_active)
        
        # Фильтр по городу
        if filters.city:
            stmt = stmt.filter(func.lower(Secondhand.city) == func.lower(filters.city))
        
        # Поиск по названию или адресу
        if filters.search:
            search_pattern = f"%{filters.search}%"
            stmt = stmt.filter(
                or_(
                    Secondhand.name.ilike(search_pattern),
                    Secondhand.address.ilike(search_pattern),
                    Secondhand.description.ilike(search_pattern),
                )
            )
        
        return stmt

    async def get_secondhands_in_bounds(
        self, 
        db: AsyncSession, 
        ne_lat: float, 
        ne_lng: float, 
        sw_lat: float, 
        sw_lng: float
    ) -> List[Secondhand]:
        try:
            stmt = select(Secondhand).filter(
                Secondhand.is_active == True,
                Secondhand.latitude.isnot(None),
                Secondhand.longitude.isnot(None),
                Secondhand.latitude.between(sw_lat, ne_lat),
                Secondhand.longitude.between(sw_lng, ne_lng)
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting secondhands in bounds: {e}")
            return []

    async def search_nearby(
        self, 
        db: AsyncSession, 
        lat: float, 
        lng: float, 
        radius_km: float = 5
    ) -> List[Secondhand]:
        try:
            # Простая прямоугольная область вокруг точки
            # В реальном проекте используем PostGIS или специальные расширения
            lat_offset = radius_km / 111.0  # примерно 1 градус = 111 км
            import math
            lng_offset = radius_km / (111.0 * abs(math.cos(math.radians(lat))))
            
            stmt = select(Secondhand).filter(
                Secondhand.is_active == True,
                Secondhand.latitude.isnot(None),
                Secondhand.longitude.isnot(None),
                Secondhand.latitude.between(lat - lat_offset, lat + lat_offset),
                Secondhand.longitude.between(lng - lng_offset, lng + lng_offset)
            )
            result = await db.execute(stmt)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error searching nearby secondhands: {e}")
            return []

    async def create_secondhand(self, db: AsyncSession, secondhand_data: SecondhandCreate) -> Secondhand:
        """
        Создать новый секондхенд
        """
        try:
            if not secondhand_data.latitude or not secondhand_data.longitude:
                latitude, longitude = self.map_service.geocode_address(
                    f"{secondhand_data.address}, {secondhand_data.city}"
                )
            else:
                latitude = secondhand_data.latitude
                longitude = secondhand_data.longitude

            db_secondhand = Secondhand(
                name=secondhand_data.name,
                address=secondhand_data.address,
                city=secondhand_data.city,
                latitude=latitude,
                longitude=longitude,
                phone=secondhand_data.phone,
                email=secondhand_data.email,
                website=secondhand_data.website,
                opening_hours=secondhand_data.opening_hours,
                description=secondhand_data.description,
                is_active=True,
            )

            db.add(db_secondhand)
            await db.commit()
            await db.refresh(db_secondhand)
            
            logger.info(f"Created secondhand: {db_secondhand.name} (ID: {db_secondhand.id})")
            return db_secondhand
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating secondhand: {e}")
            raise

    async def update_secondhand(
        self, 
        db: AsyncSession, 
        secondhand_id: int, 
        secondhand_data: SecondhandUpdate
    ) -> Optional[Secondhand]:
        try:
            db_secondhand = await self.get_secondhand_by_id(db, secondhand_id)
            if not db_secondhand:
                return None

            # Обновляем только переданные поля
            update_data = secondhand_data.model_dump(exclude_unset=True)
            
            # Если обновился адрес, перегеокодируем координаты
            if 'address' in update_data or 'city' in update_data:
                new_address = update_data.get('address', db_secondhand.address)
                new_city = update_data.get('city', db_secondhand.city)
                latitude, longitude = self.map_service.geocode_address(f"{new_address}, {new_city}")
                update_data['latitude'] = latitude
                update_data['longitude'] = longitude

            for field, value in update_data.items():
                setattr(db_secondhand, field, value)

            await db.commit()
            await db.refresh(db_secondhand)
            
            logger.info(f"Updated secondhand ID: {secondhand_id}")
            return db_secondhand
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating secondhand {secondhand_id}: {e}")
            return None

    async def delete_secondhand(self, db: AsyncSession, secondhand_id: int) -> bool:
        """
        Мягкое удаление секондхенда
        """
        try:
            db_secondhand = await self.get_secondhand_by_id(db, secondhand_id)
            if not db_secondhand:
                return False

            db_secondhand.is_active = False
            await db.commit()
            
            logger.info(f"Soft deleted secondhand ID: {secondhand_id}")
            return True
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting secondhand {secondhand_id}: {e}")
            return False

    async def get_cities(self, db: AsyncSession) -> List[str]:
        try:
            result = await db.execute(
                select(Secondhand.city)
                .where(Secondhand.is_active.is_(True))
                .distinct()
            )
            cities_rows = result.all()
            return [row[0] for row in cities_rows if row[0]]
        except Exception as e:
            logger.error(f"Error getting cities: {e}")
            return []

    def bulk_create_secondhands(self, db: Session, secondhands_data: List[SecondhandCreate]) -> List[Secondhand]:
        """
        Массовое создание секондхендов (для инициализации данных)
        """
        created = []
        try:
            for data in secondhands_data:
                secondhand = self.create_secondhand(db, data)
                if secondhand:
                    created.append(secondhand)
            
            db.commit()
            return created
        except Exception as e:
            db.rollback()
            logger.error(f"Error in bulk create: {e}")
            return []

    async def get_clusters_in_bounds(
        self,
        db: AsyncSession,
        zoom: int,
        ne_lat: float,
        ne_lng: float,
        sw_lat: float,
        sw_lng: float,
    ) -> List[MapClusterResponse]:
        """
        Получить кластеры секондхендов в границах карты для указанного zoom.
        """
        points = await self.get_secondhands_in_bounds(
            db,
            ne_lat=ne_lat,
            ne_lng=ne_lng,
            sw_lat=sw_lat,
            sw_lng=sw_lng,
        )
        return self._cluster_points(points, zoom)

    def _cell_size_for_zoom(self, zoom: int) -> float:
        if zoom <= 5:
            return 1.0
        elif zoom <= 8:
            return 0.5
        elif zoom <= 10:
            return 0.2
        elif zoom <= 12:
            return 0.1
        elif zoom <= 14:
            return 0.05
        else:
            return 0.02

    def _cluster_points(
        self,
        points: List[Secondhand],
        zoom: int,
    ) -> List[MapClusterResponse]:
        if not points:
            return []

        if zoom >= 16:
            return [
                MapClusterResponse(
                    latitude=p.latitude,
                    longitude=p.longitude,
                    count=1,
                    ids=[p.id],
                )
                for p in points
                if p.latitude is not None and p.longitude is not None
            ]

        cell_size = self._cell_size_for_zoom(zoom)
        clusters: dict[tuple[int, int], dict] = {}

        for p in points:
            if p.latitude is None or p.longitude is None:
                continue

            cell_lat = math.floor(p.latitude / cell_size)
            cell_lng = math.floor(p.longitude / cell_size)
            key = (cell_lat, cell_lng)

            if key not in clusters:
                clusters[key] = {
                    "lat_sum": 0.0,
                    "lng_sum": 0.0,
                    "count": 0,
                    "ids": [],
                }

            clusters[key]["lat_sum"] += p.latitude
            clusters[key]["lng_sum"] += p.longitude
            clusters[key]["count"] += 1
            clusters[key]["ids"].append(p.id)

        result: List[MapClusterResponse] = []
        for data in clusters.values():
            count = data["count"]
            result.append(
                MapClusterResponse(
                    latitude=data["lat_sum"] / count,
                    longitude=data["lng_sum"] / count,
                    count=count,
                    ids=data["ids"],
                )
            )

        return result

    async def get_secondhands_by_city_cached(
            self,
            db: AsyncSession,
            city: str,
    ) -> list[Secondhand]:
        """
        Часто используемый кейс: активные секонды в городе.
        Если в кэше есть — берём из кэша, иначе — из БД и кладём в кэш.
        """

        cache_key = f"{SECONDHAND_CITY_CACHE_PREFIX}{city}"

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        result = await db.execute(
            select(Secondhand).where(
                and_(
                    Secondhand.city == city,
                    Secondhand.is_active.is_(True),
                )
            )
        )
        secondhands: list[Secondhand] = result.scalars().all()

        cache.set(cache_key, secondhands)
        return secondhands

    @staticmethod
    def invalidate_secondhand_cache() -> None:
        """
        Вызываем после create/update/delete,
        чтобы кэш не содержал устаревших данных.
        """
        cache.clear_prefix(SECONDHAND_CITY_CACHE_PREFIX)