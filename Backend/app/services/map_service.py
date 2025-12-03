import requests
import logging
from typing import Tuple, Optional
from math import floor
from typing import List

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from Backend.app.models.secondhand import Secondhand
from Backend.app.schemas.secondhand import MapClusterResponse, MapPointResponse


logger = logging.getLogger(__name__)

GRID_ZOOM_CITY = 0.5   # ~широкие ячейки для маленького zoom
GRID_ZOOM_STREET = 0.1 # помельче
GRID_ZOOM_DETAILED = 0.02  # почти без агрегации


class MapService:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.geocoder_url = "https://geocode-maps.yandex.ru/1.x/"

    def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Геокодирование адреса через Яндекс.Геокодер
        Возвращает (latitude, longitude)
        """
        try:
            if not self.api_key:
                logger.warning("Yandex Maps API key not configured")
                return None, None

            params = {
                'apikey': self.api_key,
                'geocode': address,
                'format': 'json'
            }

            response = requests.get(self.geocoder_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            features = data.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])
            
            if features:
                # Берем первый результат
                pos = features[0]['GeoObject']['Point']['pos']
                lng, lat = map(float, pos.split())
                return lat, lng

            return None, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Geocoding request failed for address '{address}': {e}")
            return None, None
        except Exception as e:
            logger.error(f"Geocoding error for address '{address}': {e}")
            return None, None

    def validate_coordinates(self, lat: float, lng: float) -> bool:
        """
        Валидация координат
        """
        return (-90 <= lat <= 90) and (-180 <= lng <= 180)

    def calculate_distance(
        self, 
        lat1: float, 
        lng1: float, 
        lat2: float, 
        lng2: float
    ) -> float:
        """
        Расчет расстояния между двумя точками (упрощенная формула)
        """
        # Упрощенный расчет для небольших расстояний
        import math
        dx = (lng2 - lng1) * 111.32 * math.cos(math.radians((lat1 + lat2) / 2))
        dy = (lat2 - lat1) * 111.32
        return math.sqrt(dx*dx + dy*dy)

    async def get_map_clusters_optimized(
            self,
            db: AsyncSession,
            bounds: dict,
            zoom: int,
    ) -> List[MapClusterResponse]:
        """
        Оптимизированный выбор кластеров в зависимости от zoom.

        bounds = {
            "ne_lat": ...,
            "ne_lng": ...,
            "sw_lat": ...,
            "sw_lng": ...,
        }
        """

        if zoom <= 10:
            # городской уровень
            return await self._get_clusters(db, bounds, cell_size=GRID_ZOOM_CITY)
        elif zoom <= 14:
            # районный
            return await self._get_clusters(db, bounds, cell_size=GRID_ZOOM_STREET)
        else:
            # почти детальный — можно вернуть просто точки
            # либо мелкие кластеры
            return await self._get_clusters(db, bounds, cell_size=GRID_ZOOM_DETAILED)

    async def _get_clusters(
            self,
            db: AsyncSession,
            bounds: dict,
            cell_size: float,
    ) -> List[MapClusterResponse]:
        """
        Общий метод: берём все секонды в пределах bounds,
        группируем в "квадратики" с шагом cell_size.
        """

        ne_lat = bounds["ne_lat"]
        ne_lng = bounds["ne_lng"]
        sw_lat = bounds["sw_lat"]
        sw_lng = bounds["sw_lng"]

        # 1. Достаём все активные секонды в прямоугольнике
        result = await db.execute(
            select(Secondhand).where(
                and_(
                    Secondhand.is_active.is_(True),
                    Secondhand.latitude.is_not(None),
                    Secondhand.longitude.is_not(None),
                    Secondhand.latitude >= sw_lat,
                    Secondhand.latitude <= ne_lat,
                    Secondhand.longitude >= sw_lng,
                    Secondhand.longitude <= ne_lng,
                )
            )
        )
        secondhands: list[Secondhand] = result.scalars().all()

        if not secondhands:
            return []

        # 2. Группируем по "ячейкам"
        buckets: dict[tuple[int, int], list[Secondhand]] = {}

        for sh in secondhands:
            lat = sh.latitude
            lng = sh.longitude
            if lat is None or lng is None:
                continue

            key = (
                floor(lat / cell_size),
                floor(lng / cell_size),
            )
            buckets.setdefault(key, []).append(sh)

        # 3. Считаем центры кластеров
        clusters: list[MapClusterResponse] = []

        for (lat_idx, lng_idx), items in buckets.items():
            center_lat = (lat_idx + 0.5) * cell_size
            center_lng = (lng_idx + 0.5) * cell_size
            clusters.append(
                MapClusterResponse(
                    latitude=center_lat,
                    longitude=center_lng,
                    count=len(items),
                )
            )

        return clusters

    async def get_detailed_points(
            self,
            db: AsyncSession,
            bounds: dict,
    ) -> List[MapPointResponse]:
        """
        Если нужен прям детальный список точек (для большого zoom).
        """

        ne_lat = bounds["ne_lat"]
        ne_lng = bounds["ne_lng"]
        sw_lat = bounds["sw_lat"]
        sw_lng = bounds["sw_lng"]

        result = await db.execute(
            select(Secondhand).where(
                and_(
                    Secondhand.is_active.is_(True),
                    Secondhand.latitude.is_not(None),
                    Secondhand.longitude.is_not(None),
                    Secondhand.latitude >= sw_lat,
                    Secondhand.latitude <= ne_lat,
                    Secondhand.longitude >= sw_lng,
                    Secondhand.longitude <= ne_lng,
                )
            )
        )
        secondhands: list[Secondhand] = result.scalars().all()

        points: list[MapPointResponse] = []
        for sh in secondhands:
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