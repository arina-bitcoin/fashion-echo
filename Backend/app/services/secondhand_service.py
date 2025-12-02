from typing import List, Optional, Tuple
import logging
import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func

from Backend.app.models.secondhand import Secondhand
from Backend.app.schemas.secondhand import (
    SecondhandCreate,
    SecondhandUpdate,
    SecondhandFilters,
    MapClusterResponse,
)
from Backend.app.services.map_service import MapService

logger = logging.getLogger(__name__)


class SecondhandService:
    def __init__(self):
        self.map_service = MapService()

    async def get_secondhand_by_id(
        self,
        db: AsyncSession,
        secondhand_id: int,
    ) -> Optional[Secondhand]:
        try:
            result = await db.execute(
                select(Secondhand).where(
                    Secondhand.id == secondhand_id,
                    Secondhand.is_active.is_(True),
                )
            )
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
            query = select(Secondhand)
            query = self._apply_filters(query, filters)

            count_query = select(func.count()).select_from(
                self._apply_filters(select(Secondhand), filters).subquery()
            )
            total_result = await db.execute(count_query)
            total = total_result.scalar_one() or 0

            query = query.order_by(Secondhand.name.asc()).offset(skip).limit(limit)
            result = await db.execute(query)
            items = result.scalars().all()

            return items, total
        except Exception as e:
            logger.error(f"Error getting secondhands: {e}")
            return [], 0

    def _apply_filters(self, query, filters: SecondhandFilters):
        if filters.is_active is not None:
            query = query.where(Secondhand.is_active == filters.is_active)

        if filters.city:
            query = query.where(
                func.lower(Secondhand.city) == func.lower(filters.city)
            )

        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.where(
                or_(
                    Secondhand.name.ilike(search_pattern),
                    Secondhand.address.ilike(search_pattern),
                    Secondhand.description.ilike(search_pattern),
                )
            )

        return query

    async def get_secondhands_in_bounds(
        self,
        db: AsyncSession,
        ne_lat: float,
        ne_lng: float,
        sw_lat: float,
        sw_lng: float,
    ) -> List[Secondhand]:
        try:
            query = (
                select(Secondhand)
                .where(Secondhand.is_active.is_(True))
                .where(Secondhand.latitude.is_not(None))
                .where(Secondhand.longitude.is_not(None))
                .where(Secondhand.latitude.between(sw_lat, ne_lat))
                .where(Secondhand.longitude.between(sw_lng, ne_lng))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting secondhands in bounds: {e}")
            return []

    async def search_nearby(
        self,
        db: AsyncSession,
        lat: float,
        lng: float,
        radius_km: float = 5,
    ) -> List[Secondhand]:
        try:
            lat_offset = radius_km / 111.0
            # для простоты игнорируем cos(lat), можно упростить:
            lng_offset = radius_km / 111.0

            query = (
                select(Secondhand)
                .where(Secondhand.is_active.is_(True))
                .where(Secondhand.latitude.is_not(None))
                .where(Secondhand.longitude.is_not(None))
                .where(Secondhand.latitude.between(lat - lat_offset, lat + lat_offset))
                .where(Secondhand.longitude.between(lng - lng_offset, lng + lng_offset))
            )
            result = await db.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error searching nearby secondhands: {e}")
            return []

    async def create_secondhand(
        self,
        db: AsyncSession,
        secondhand_data: SecondhandCreate,
    ) -> Secondhand:
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

            logger.info(
                f"Created secondhand: {db_secondhand.name} (ID: {db_secondhand.id})"
            )
            return db_secondhand
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating secondhand: {e}")
            raise

    async def update_secondhand(
        self,
        db: AsyncSession,
        secondhand_id: int,
        secondhand_data: SecondhandUpdate,
    ) -> Optional[Secondhand]:
        try:
            db_secondhand = await self.get_secondhand_by_id(db, secondhand_id)
            if not db_secondhand:
                return None

            update_data = secondhand_data.model_dump(exclude_unset=True)

            if "address" in update_data or "city" in update_data:
                new_address = update_data.get("address", db_secondhand.address)
                new_city = update_data.get("city", db_secondhand.city)
                latitude, longitude = self.map_service.geocode_address(
                    f"{new_address}, {new_city}"
                )
                update_data["latitude"] = latitude
                update_data["longitude"] = longitude

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

    async def delete_secondhand(
        self,
        db: AsyncSession,
        secondhand_id: int,
    ) -> bool:
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

    async def get_clusters_in_bounds(
        self,
        db: AsyncSession,
        zoom: int,
        ne_lat: float,
        ne_lng: float,
        sw_lat: float,
        sw_lng: float,
    ) -> List[MapClusterResponse]:
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
