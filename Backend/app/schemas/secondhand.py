from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


# Enums для валидации
class DayOfWeek(str, Enum):
    MONDAY = "mon"
    TUESDAY = "tue"
    WEDNESDAY = "wed"
    THURSDAY = "thu"
    FRIDAY = "fri"
    SATURDAY = "sat"
    SUNDAY = "sun"


# Базовые схемы
class SecondhandBase(BaseModel):
    """Базовая схема для секондхенда"""
    name: str = Field(..., min_length=1, max_length=200, description="Название магазина")
    address: str = Field(..., min_length=1, max_length=500, description="Полный адрес")
    city: str = Field(..., min_length=1, max_length=100, description="Город")
    phone: Optional[str] = Field(None, max_length=20, description="Телефон")
    email: Optional[str] = Field(None, max_length=100, description="Email")
    website: Optional[str] = Field(None, max_length=200, description="Веб-сайт")
    description: Optional[str] = Field(None, description="Описание магазина")

    @field_validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v

    @field_validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.replace('+', '').replace(' ', '').replace('-', '').isdigit():
            raise ValueError('Phone must contain only digits and valid symbols')
        return v


class SecondhandCreate(SecondhandBase):
    """Схема для создания секондхенда"""
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Широта")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Долгота")
    opening_hours: Optional[Dict[str, str]] = Field(
        None, 
        description="Часы работы в формате {'mon': '10:00-20:00', ...}"
    )

    @field_validator('opening_hours')
    def validate_opening_hours(cls, v):
        if v is not None:
            valid_days = [day.value for day in DayOfWeek]
            for day in v.keys():
                if day not in valid_days:
                    raise ValueError(f'Invalid day: {day}. Must be one of {valid_days}')
        return v


class SecondhandUpdate(BaseModel):
    """Схема для обновления секондхенда (все поля опциональны)"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    opening_hours: Optional[Dict[str, str]] = Field(None)
    description: Optional[str] = Field(None)
    is_active: Optional[bool] = Field(None)

    @field_validator('email')
    def validate_email(cls, v):
        if v is not None and '@' not in v:
            raise ValueError('Invalid email format')
        return v


# Response схемы
class SecondhandResponse(SecondhandBase):
    """Схема для ответа с полной информацией о секондхенде"""
    id: int
    latitude: Optional[float]
    longitude: Optional[float]
    opening_hours: Optional[Dict[str, str]]
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "name": "Fashion Recycle",
                "address": "Москва, ул. Тверская, 10",
                "city": "Москва",
                "latitude": 55.7558,
                "longitude": 37.6173,
                "phone": "+7 495 123-45-67",
                "email": "info@fashion-recycle.ru",
                "website": "https://fashion-recycle.ru",
                "opening_hours": {
                    "mon": "10:00-20:00",
                    "tue": "10:00-20:00",
                    "wed": "10:00-20:00",
                    "thu": "10:00-20:00",
                    "fri": "10:00-21:00",
                    "sat": "11:00-19:00",
                    "sun": "11:00-18:00"
                },
                "description": "Экологичный секондхенд с качественной одеждой",
                "is_active": True,
                "created_at": "2024-01-15T10:00:00"
            }
        }


class MapPointResponse(BaseModel):
    """Упрощенная схема для отображения на карте"""
    id: int
    name: str
    latitude: float
    longitude: float
    address: str
    phone: Optional[str]

    class Config:
        orm_mode = True


class SecondhandSearchResponse(BaseModel):
    """Схема для ответа поиска с пагинацией"""
    items: List[SecondhandResponse]
    total: int
    skip: int
    limit: int


# Схемы для фильтров
class SecondhandFilters(BaseModel):
    """Схема для параметров фильтрации секондхендов"""
    city: Optional[str] = None
    search: Optional[str] = None
    is_active: Optional[bool] = True

    class Config:
        use_enum_values = True


class MapBoundsFilters(BaseModel):
    """Схема для параметров границ карты"""
    ne_lat: float = Field(..., ge=-90, le=90)
    ne_lng: float = Field(..., ge=-180, le=180)
    sw_lat: float = Field(..., ge=-90, le=90)
    sw_lng: float = Field(..., ge=-180, le=180)

    @field_validator('ne_lat', 'sw_lat')
    def validate_latitudes(cls, v, values, **kwargs):
        if 'ne_lat' in values and 'sw_lat' in values:
            if values['ne_lat'] <= values['sw_lat']:
                raise ValueError('ne_lat must be greater than sw_lat')
        return v