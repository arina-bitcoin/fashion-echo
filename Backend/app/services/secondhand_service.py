from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional, Tuple
import logging

from Backend.app.models.secondhand import Secondhand
from Backend.app.schemas.secondhand import (
    SecondhandCreate, 
    SecondhandUpdate, 
    SecondhandFilters
)
from Backend.app.services.map_service import MapService

logger = logging.getLogger(__name__)


class SecondhandService:
    def __init__(self):
        self.map_service = MapService()

    def get_secondhand_by_id(self, db: Session, secondhand_id: int) -> Optional[Secondhand]:
        """
        Получить секондхенд по ID
        """
        try:
            return db.query(Secondhand).filter(
                Secondhand.id == secondhand_id,
                Secondhand.is_active == True
            ).first()
        except Exception as e:
            logger.error(f"Error getting secondhand by id {secondhand_id}: {e}")
            return None

    def get_secondhands(
        self, 
        db: Session, 
        filters: SecondhandFilters,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Secondhand], int]:
        """
        Получить список секондхендов с фильтрацией и пагинацией
        """
        try:
            query = db.query(Secondhand)
            
            # Применяем фильтры
            query = self._apply_filters(query, filters)
            
            # Получаем общее количество для пагинации
            total = query.count()
            
            # Применяем пагинацию и сортировку
            items = query.order_by(Secondhand.name.asc()).offset(skip).limit(limit).all()
            
            return items, total
            
        except Exception as e:
            logger.error(f"Error getting secondhands: {e}")
            return [], 0

    def _apply_filters(self, query, filters: SecondhandFilters):
        """
        Применить фильтры к запросу
        """
        # Фильтр по активности
        if filters.is_active is not None:
            query = query.filter(Secondhand.is_active == filters.is_active)
        
        # Фильтр по городу
        if filters.city:
            query = query.filter(func.lower(Secondhand.city) == func.lower(filters.city))
        
        # Поиск по названию или адресу
        if filters.search:
            search_pattern = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Secondhand.name.ilike(search_pattern),
                    Secondhand.address.ilike(search_pattern),
                    Secondhand.description.ilike(search_pattern)
                )
            )
        
        return query

    def get_secondhands_in_bounds(
        self, 
        db: Session, 
        ne_lat: float, 
        ne_lng: float, 
        sw_lat: float, 
        sw_lng: float
    ) -> List[Secondhand]:
        """
        Получить секондхенды в границах карты
        """
        try:
            return db.query(Secondhand).filter(
                Secondhand.is_active == True,
                Secondhand.latitude.isnot(None),
                Secondhand.longitude.isnot(None),
                Secondhand.latitude.between(sw_lat, ne_lat),
                Secondhand.longitude.between(sw_lng, ne_lng)
            ).all()
        except Exception as e:
            logger.error(f"Error getting secondhands in bounds: {e}")
            return []

    def search_nearby(
        self, 
        db: Session, 
        lat: float, 
        lng: float, 
        radius_km: float = 5
    ) -> List[Secondhand]:
        """
        Поиск секондхендов в радиусе от точки (упрощенная версия)
        """
        try:
            # Простая прямоугольная область вокруг точки
            # В реальном проекте используем PostGIS или специальные расширения
            lat_offset = radius_km / 111.0  # примерно 1 градус = 111 км
            lng_offset = radius_km / (111.0 * abs(func.cos(func.radians(lat))))
            
            return db.query(Secondhand).filter(
                Secondhand.is_active == True,
                Secondhand.latitude.isnot(None),
                Secondhand.longitude.isnot(None),
                Secondhand.latitude.between(lat - lat_offset, lat + lat_offset),
                Secondhand.longitude.between(lng - lng_offset, lng + lng_offset)
            ).all()
        except Exception as e:
            logger.error(f"Error searching nearby secondhands: {e}")
            return []

    def create_secondhand(self, db: Session, secondhand_data: SecondhandCreate) -> Secondhand:
        """
        Создать новый секондхенд
        """
        try:
            # Если координаты не указаны, пытаемся геокодировать адрес
            if not secondhand_data.latitude or not secondhand_data.longitude:
                latitude, longitude = self.map_service.geocode_address(
                    f"{secondhand_data.address}, {secondhand_data.city}"
                )
            else:
                latitude = secondhand_data.latitude
                longitude = secondhand_data.longitude

            # Создаем объект секондхенда
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
                is_active=True
            )
            
            db.add(db_secondhand)
            db.commit()
            db.refresh(db_secondhand)
            
            logger.info(f"Created secondhand: {db_secondhand.name} (ID: {db_secondhand.id})")
            return db_secondhand
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating secondhand: {e}")
            raise

    def update_secondhand(
        self, 
        db: Session, 
        secondhand_id: int, 
        secondhand_data: SecondhandUpdate
    ) -> Optional[Secondhand]:
        """
        Обновить информацию о секондхенде
        """
        try:
            db_secondhand = self.get_secondhand_by_id(db, secondhand_id)
            if not db_secondhand:
                return None

            # Обновляем только переданные поля
            update_data = secondhand_data.dict(exclude_unset=True)
            
            # Если обновился адрес, перегеокодируем координаты
            if 'address' in update_data or 'city' in update_data:
                new_address = update_data.get('address', db_secondhand.address)
                new_city = update_data.get('city', db_secondhand.city)
                latitude, longitude = self.map_service.geocode_address(f"{new_address}, {new_city}")
                update_data['latitude'] = latitude
                update_data['longitude'] = longitude

            for field, value in update_data.items():
                setattr(db_secondhand, field, value)

            db.commit()
            db.refresh(db_secondhand)
            
            logger.info(f"Updated secondhand ID: {secondhand_id}")
            return db_secondhand
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating secondhand {secondhand_id}: {e}")
            return None

    def delete_secondhand(self, db: Session, secondhand_id: int) -> bool:
        """
        Мягкое удаление секондхенда
        """
        try:
            db_secondhand = self.get_secondhand_by_id(db, secondhand_id)
            if not db_secondhand:
                return False

            db_secondhand.is_active = False
            db.commit()
            
            logger.info(f"Soft deleted secondhand ID: {secondhand_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting secondhand {secondhand_id}: {e}")
            return False

    def get_cities(self, db: Session) -> List[str]:
        """
        Получить список всех городов, где есть секондхенды
        """
        try:
            cities = db.query(Secondhand.city).filter(
                Secondhand.is_active == True
            ).distinct().all()
            
            return [city[0] for city in cities if city[0]]
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