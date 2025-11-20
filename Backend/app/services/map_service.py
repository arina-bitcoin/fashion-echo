# backend/app/services/map_service.py
import requests
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


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