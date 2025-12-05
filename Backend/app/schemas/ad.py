from pydantic import BaseModel, field_validator, Field, ConfigDict, ValidationInfo
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ================== Enum'ы ==================

class AdStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"


class AdType(str, Enum):
    """Типы объявлений"""
    SELL = "sell"
    EXCHANGE = "exchange"
    BUY = "buy"


class AdCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_REPAIR = "needs_repair"


class SortBy(str, Enum):
    NEWEST = "newest"          # Сначала новые
    OLDEST = "oldest"          # Сначала старые
    PRICE_ASC = "price_asc"    # Сначала дешёвые
    PRICE_DESC = "price_desc"  # Сначала дорогие
    POPULAR = "popular"        # По популярности


class Condition(str, Enum):
    """Состояние одежды"""
    NEW = "new"                   # Новая с биркой
    EXCELLENT = "excellent"       # Отличное состояние
    GOOD = "good"                 # Хорошее состояние
    SATISFACTORY = "satisfactory" # Удовлетворительное
    NEEDS_REPAIR = "needs_repair" # Требует ремонта


# ================== User для ответа ==================

class UserResponseSimple(BaseModel):
    """Упрощенная схема пользователя для ответов"""
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ================== Базовые схемы объявления ==================

class AdBase(BaseModel):
    type: AdType
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    price: Optional[float] = Field(None, ge=0)
    condition: Optional[str] = None

    # Категории
    main_category: Optional[str] = Field(None, description="Основная категория")
    sub_category: Optional[str] = Field(None, description="Подкатегория")
    season: Optional[str] = Field(None, description="Сезон")

    # Размер и цвет
    size: Optional[str] = Field(None, max_length=50)
    colors: Optional[list[str]] = Field(default_factory=list)

    # Теги для поиска
    tags: Optional[str] = Field(None, description="Ключевые слова для поиска")

    # Бренд
    brand: Optional[str] = Field(None, max_length=100)


class AdCreate(AdBase):
    @field_validator('price')
    def validate_price(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        # Для типа SELL цена обязательна
        if info.data and info.data.get('type') == AdType.SELL and v is None:
            raise ValueError('Цена обязательна для продажи')
        if v is not None and v < 0:
            raise ValueError('Цена не может быть отрицательной')
        return v


class AdUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    price: Optional[float] = Field(None, ge=0)
    condition: Optional[str] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    season: Optional[str] = None
    size: Optional[str] = None
    colors: Optional[list[str]] = None
    tags: Optional[str] = None
    location: Optional[str] = None
    is_negotiable: Optional[bool] = None
    brand: Optional[str] = None
    # вместо is_active используем статус
    status: Optional[AdStatus] = None


class AdResponse(AdBase):
    id: int
    title: str
    description: str
    price: Optional[float] = None
    type: str
    status: str

    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    season: Optional[str] = None
    condition: Optional[str] = None
    size: Optional[str] = None
    colors: Optional[list[str]] = None
    tags: Optional[str] = None
    brand: Optional[str] = None

    view_count: int = 0
    favorite_count: int = 0
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    images: Optional[list[str]] = Field(default_factory=list, description="URL-ы изображений")
    user: Optional[UserResponseSimple] = None
    is_favorite: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class AdStatusResponse(BaseModel):
    message: str
    ad_id: int
    status: str


# ================== Поиск объявлений ==================

class AdSearch(BaseModel):
    """Схема для расширенного поиска объявлений"""

    # 1. Статус объявления
    status: Optional[AdStatus] = Field(AdStatus.ACTIVE, description="Статус объявления")

    # 2. Тип объявления
    ad_type: Optional[str] = Field(
        None,
        pattern="^(sell|buy|exchange)$",
        description="Тип объявления"
    )

    # 3. Основные категории (можно несколько)
    main_categories: Optional[list[str]] = Field(None, description="Основные категории")

    # 4. Подкатегории (можно несколько)
    sub_categories: Optional[list[str]] = Field(None, description="Подкатегории")

    # 5. Сезонные категории (можно несколько)
    seasons: Optional[list[str]] = Field(None, description="Сезонные категории")

    # 6. Ценовой диапазон
    min_price: Optional[float] = Field(None, ge=0, description="Минимальная цена")
    max_price: Optional[float] = Field(None, ge=0, description="Максимальная цена")

    # 7. Состояние товара (можно несколько)
    conditions: Optional[list[str]] = Field(None, description="Состояние товара")

    # 8. Размеры (можно несколько)
    sizes: Optional[list[str]] = Field(None, description="Размеры")

    # 9. Цвета (можно несколько)
    colors: Optional[list[str]] = Field(None, description="Цвета")

    # 10. Текстовый поиск
    query: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Текстовый поиск"
    )

    # 11. Сортировка
    sort_by: Optional[SortBy] = Field(SortBy.NEWEST, description="Сортировка")

    # Пагинация
    skip: int = Field(0, ge=0, description="Пропустить записей")
    limit: int = Field(50, ge=1, le=200, description="Лимит записей")

    # Дополнительные фильтры
    user_id: Optional[int] = Field(None, description="Фильтр по пользователю")
    has_images: Optional[bool] = Field(None, description="Только с изображениями")
    is_negotiable: Optional[bool] = Field(None, description="Возможен торг")

    @field_validator('max_price')
    def validate_price_range(cls, v, values):
        """Валидация ценового диапазона"""
        min_price = values.get('min_price')
        if v is not None and min_price is not None and v < min_price:
            raise ValueError('max_price должен быть больше или равен min_price')
        return v

    @field_validator('main_categories', 'sub_categories', 'seasons', 'conditions', 'sizes', 'colors')
    def validate_list_fields(cls, v):
        """Валидация списков - удаляем пустые строки и дубликаты"""
        if v is not None:
            v = [item for item in v if item and str(item).strip()]
            v = list(dict.fromkeys(v))
        return v

    @field_validator('colors')
    def validate_colors(cls, v):
        """Валидация цветов"""
        valid_colors = {
            "black", "white", "gray", "red", "blue", "green",
            "yellow", "pink", "purple", "brown", "orange",
            "beige", "multicolor"
        }
        if v is not None:
            invalid = [color for color in v if color.lower() not in valid_colors]
            if invalid:
                raise ValueError(f"Недопустимые цвета: {invalid}")
        return v

    # Упрощённые методы для пагинации/сортировки

    def get_skip(self) -> int:
        """offset для пагинации"""
        return self.skip

    def get_limit(self) -> int:
        """limit для пагинации"""
        return self.limit

    def get_sort_by(self) -> list[str]:
        """Возвращает параметры сортировки в виде SQL-выражений"""
        sort_mapping = {
            SortBy.NEWEST: "created_at DESC",
            SortBy.OLDEST: "created_at ASC",
            SortBy.PRICE_ASC: "price ASC",
            SortBy.PRICE_DESC: "price DESC",
            SortBy.POPULAR: "((view_count * 0.5) + (favorite_count * 0.5)) DESC",
        }
        return [sort_mapping.get(self.sort_by or SortBy.NEWEST, "created_at DESC")]


# ================== Избранное и картинки ==================

class FavoriteResponse(BaseModel):
    ad_id: int
    user_id: int
    added: bool
    message: str


class ImageUploadResponse(BaseModel):
    file_path: str
    filename: str
    url: str
    size: int
    image_id: Optional[int] = None
    order: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ImageOrderUpdate(BaseModel):
    image_ids: list[int] = Field(
        ...,
        min_items=1,
        description="Список ID изображений в новом порядке"
    )
