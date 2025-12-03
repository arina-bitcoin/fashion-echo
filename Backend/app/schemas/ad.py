from pydantic import BaseModel, field_validator, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class AdType(str, Enum):
    """Типы объявлений"""
    SELL = "sell"
    EXCHANGE = "exchange"
    BUY = "buy"

class AdBase(BaseModel):
    type: AdType
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    condition: str
    category: str
    size: Optional[str] = None
    brand: Optional[str] = None

class AdCreate(AdBase):
    @field_validator('price')
    def validate_price(cls, v, values):
        if values.get('type') == AdType.SELL and v is None:
            raise ValueError('Price is required for sell ads')
        return v

class AdUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None

class AdResponse(AdBase):
    id: int
    user_id: int
    images: list[str] = []
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Enum для сортировки
class SortBy(str, Enum):
    NEWEST = "newest"          # Сначала новые
    OLDEST = "oldest"          # Сначала старые
    PRICE_ASC = "price_asc"    # Сначала дешёвые
    PRICE_DESC = "price_desc"  # Сначала дорогие
    POPULAR = "popular"        # По популярности

# Enum для статуса
class AdStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ALL = "all"

# ---------- Enum для категорий одежды ----------
# class ClothingCategory(str, Enum):
#     """Категории одежды по полу/возрасту"""
    
#     # Основные категории
#     MENS = "mens"              # Мужская одежда
#     WOMENS = "womens"          # Женская одежда
#     KIDS = "kids"              # Детская одежда
#     UNISEX = "unisex"          # Унисекс
#     BABY = "baby"              # Одежда для младенцев
    
#     # Подкатегории (можно комбинировать с основными)
#     # Например: "mens,formal" или "womens,summer"
#     FORMAL = "formal"          # Деловая/формальная
#     CASUAL = "casual"          # Повседневная
#     SPORTS = "sports"          # Спортивная
#     OUTERWEAR = "outerwear"    # Верхняя одежда
#     UNDERWEAR = "underwear"    # Нижнее белье
#     SWIMWEAR = "swimwear"      # Купальники/плавки
#     ACCESSORIES = "accessories" # Аксессуары
#     SHOES = "shoes"            # Обувь
#     BAGS = "bags"              # Сумки
#     JEWELRY = "jewelry"        # Украшения
    
#     # Сезонность
#     SUMMER = "summer"          # Летняя
#     WINTER = "winter"          # Зимняя
#     AUTUMN = "autumn"          # Осенняя  
#     SPRING = "spring"          # Весенняя
#     ALL_SEASON = "all_season"  # Всесезонная

# ---------- Enum для состояний одежды ----------
class Condition(str, Enum):
    """Состояние одежды"""
    NEW = "new"                # Новая с биркой
    LIKE_NEW = "like_new"      # Как новая
    EXCELLENT = "excellent"    # Отличное состояние
    GOOD = "good"              # Хорошее состояние
    SATISFACTORY = "satisfactory" # Удовлетворительное
    NEEDS_REPAIR = "needs_repair" # Требует ремонта

# class MultiSort(BaseModel):
#     """Модель для сортировки по нескольким критериям"""
    
#     primary: SortBy = Field(default=SortBy.NEWEST, description="Основной критерий сортировки")
#     secondary: Optional[SortBy] = Field(None, description="Вторичный критерий (при равенстве primary)")
#     tertiary: Optional[SortBy] = Field(None, description="Третичный критерий (при равенстве primary и secondary)")
    
#     @field_validator('secondary', 'tertiary')
#     def validate_unique_sort_fields(cls, v, values, field):
#         """Проверяем, что критерии не повторяются"""
#         if v:
#             # Проверяем, что значение не равно primary
#             if 'primary' in values and v == values['primary']:
#                 raise ValueError(f"{field.name} не может быть таким же как primary")
            
#             # Проверяем для tertiary, что не равен secondary
#             if field.name == 'tertiary' and 'secondary' in values:
#                 if v == values.get('secondary'):
#                     raise ValueError("tertiary не может быть таким же как secondary")
#         return v
    
#     def get_sort_expressions(self):
#         """Возвращает список выражений для сортировки в правильном порядке"""
#         sort_mapping = {
#             SortBy.NEWEST: "created_at DESC",
#             SortBy.OLDEST: "created_at ASC",
#             SortBy.PRICE_ASC: "price ASC",
#             SortBy.PRICE_DESC: "price DESC",
#             SortBy.POPULAR: "((view_count * 0.5) + (favorite_count * 0.5)) DESC",
#             SortBy.RECENTLY_VIEWED: "last_viewed DESC",
#             SortBy.RECENTLY_UPDATED: "updated_at DESC",
#             SortBy.EXPIRING_SOON: "expires_at ASC",
#             SortBy.NEAREST: "distance ASC"  # Предполагается, что distance вычисляется отдельно
#         }
        
#         expressions = []
#         if self.primary in sort_mapping:
#             expressions.append(sort_mapping[self.primary])
#         if self.secondary and self.secondary in sort_mapping:
#             expressions.append(sort_mapping[self.secondary])
#         if self.tertiary and self.tertiary in sort_mapping:
#             expressions.append(sort_mapping[self.tertiary])
        
#         return expressions

# class SortRequest(BaseModel):
#     """Запрос на сортировку (для API)"""
#     sort: Optional[MultiSort] = Field(default=None, description="Параметры сортировки")
    
#     # Альтернативный упрощенный вариант для обратной совместимости
#     sort_by: Optional[SortBy] = Field(default=None, description="Упрощенная сортировка (один параметр)")
    
#     @field_validator('sort_by')
#     def validate_sort_fields(cls, v, values):
#         """Проверяем, что не переданы оба параметра сортировки"""
#         if v and values.get('sort'):
#             raise ValueError("Используйте либо 'sort', либо 'sort_by', но не оба одновременно")
#         return v
    
# # fashion__eco\Backend\app\schemas\ad.py

# class CategoryFilter(BaseModel):
#     """Модель для фильтрации по категориям"""
    
#     main_categories: Optional[list[ClothingCategory]] = Field(
#         default=None,
#         description="Основные категории: mens, womens, kids, etc"
#     )
    
#     subcategories: Optional[list[ClothingCategory]] = Field(
#         default=None,
#         description="Подкатегории: formal, casual, sports, etc"
#     )
    
#     seasons: Optional[list[ClothingCategory]] = Field(
#         default=None,
#         description="Сезонность: summer, winter, etc"
#     )
    
#     @field_validator('main_categories', 'subcategories', 'seasons', each_item=True)
#     def validate_category_groups(cls, v, field):
#         """Проверяем, что категории принадлежат правильным группам"""
#         if field.name == 'main_categories':
#             allowed = {ClothingCategory.MENS, ClothingCategory.WOMENS, 
#                       ClothingCategory.KIDS, ClothingCategory.UNISEX, ClothingCategory.BABY}
#             if v not in allowed:
#                 raise ValueError(f"Категория {v} не является основной")
                
#         elif field.name == 'subcategories':
#             allowed = {ClothingCategory.FORMAL, ClothingCategory.CASUAL, 
#                       ClothingCategory.SPORTS, ClothingCategory.OUTERWEAR,
#                       ClothingCategory.UNDERWEAR, ClothingCategory.SWIMWEAR,
#                       ClothingCategory.ACCESSORIES, ClothingCategory.SHOES,
#                       ClothingCategory.BAGS, ClothingCategory.JEWELRY}
#             if v not in allowed:
#                 raise ValueError(f"Категория {v} не является подкатегорией")
                
#         elif field.name == 'seasons':
#             allowed = {ClothingCategory.SUMMER, ClothingCategory.WINTER,
#                       ClothingCategory.AUTUMN, ClothingCategory.SPRING,
#                       ClothingCategory.ALL_SEASON}
#             if v not in allowed:
#                 raise ValueError(f"Категория {v} не является сезонной")
#         return v
    
#     def get_filter_conditions(self):
#         """Возвращает условия для фильтрации по категориям"""
#         conditions = []
        
#         if self.main_categories:
#             # Объединяем через OR для каждой основной категории
#             main_conditions = []
#             for category in self.main_categories:
#                 main_conditions.append(f"category LIKE '%{category.value}%'")
            
#             if main_conditions:
#                 conditions.append(f"({' OR '.join(main_conditions)})")
        
#         if self.subcategories:
#             sub_conditions = []
#             for category in self.subcategories:
#                 sub_conditions.append(f"category LIKE '%{category.value}%'")
            
#             if sub_conditions:
#                 conditions.append(f"({' OR '.join(sub_conditions)})")
        
#         if self.seasons:
#             season_conditions = []
#             for category in self.seasons:
#                 season_conditions.append(f"tags LIKE '%{category.value}%'")
            
#             if season_conditions:
#                 conditions.append(f"({' OR '.join(season_conditions)})")
        
#         return conditions
    
# class AdSearch(BaseModel):
#     """Модель для расширенного поиска объявлений"""
    
#     # Текстовый поиск
#     query: Optional[str] = Field(
#         None, 
#         min_length=1, 
#         max_length=200,
#         description="Поиск по тексту в названии, описании и тегах"
#     )
    
#     # Фильтры по цене
#     min_price: Optional[float] = Field(
#         None, 
#         ge=0,
#         description="Минимальная цена"
#     )
#     max_price: Optional[float] = Field(
#         None, 
#         ge=0,
#         description="Максимальная цена"
#     )
    
#     # Фильтры по типу
#     ad_types: Optional[list[AdType]] = Field(
#         None,
#         description="Типы объявлений (можно несколько)"
#     )
    
#     # Фильтр по состоянию
#     conditions: Optional[list[Condition]] = Field(
#         None,
#         description="Состояние товара (можно несколько)"
#     )
    
#     # Фильтр по размеру
#     sizes: Optional[list[str]] = Field(
#         None,
#         description="Размеры одежды (XS, S, M, L, XL и т.д.)"
#     )
    
#     # Фильтр по бренду
#     brands: Optional[list[str]] = Field(
#         None,
#         description="Бренды одежды"
#     )
    
#     # Фильтр по цвету
#     colors: Optional[list[str]] = Field(
#         None,
#         description="Цвета"
#     )
    
#     # Фильтр по местоположению
#     location: Optional[str] = Field(
#         None,
#         description="Город или район"
#     )
    
#     # Фильтр по радиусу (если есть координаты)
#     radius_km: Optional[float] = Field(
#         None,
#         ge=0,
#         le=100,
#         description="Радиус поиска в километрах (требуются координаты)"
#     )
    
#     # Фильтр по дате
#     created_after: Optional[str] = Field(
#         None,
#         description="Объявления созданные после даты (YYYY-MM-DD)"
#     )
#     created_before: Optional[str] = Field(
#         None,
#         description="Объявления созданные до даты (YYYY-MM-DD)"
#     )
    
#     # Сложная фильтрация по категориям
#     categories: Optional[CategoryFilter] = Field(
#         None,
#         description="Фильтрация по категориям одежды"
#     )
    
#     # Сложная сортировка
#     sorting: Optional[SortRequest] = Field(
#         None,
#         description="Параметры сортировки"
#     )
    
#     # Пагинация
#     page: int = Field(
#         default=1,
#         ge=1,
#         description="Номер страницы"
#     )
#     per_page: int = Field(
#         default=20,
#         ge=1,
#         le=100,
#         description="Количество элементов на странице"
#     )
    
#     # Дополнительные фильтры
#     only_active: bool = Field(
#         default=True,
#         description="Только активные объявления"
#     )
#     only_with_images: bool = Field(
#         default=False,
#         description="Только с фотографиями"
#     )
#     only_negotiable: Optional[bool] = Field(
#         None,
#         description="Только с возможностью торга"
#     )
#     only_fresh: Optional[bool] = Field(
#         None,
#         description="Только свежие (созданные за последние 7 дней)"
#     )

class AdSearch(BaseModel):
    """Схема для расширенного поиска объявлений"""
    
    # 1. Статус объявления
    status: Optional[AdStatus] = Field(AdStatus.ACTIVE, description="Статус объявления")
    
    # 2. Тип объявления
    ad_type: Optional[str] = Field(None, pattern="^(sell|buy|exchange)$", description="Тип объявления")
    
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
    query: Optional[str] = Field(None, min_length=1, max_length=200, description="Текстовый поиск")
    
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
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price должен быть больше или равен min_price')
        return v
    
    @field_validator('main_categories', 'sub_categories', 'seasons', 'conditions', 'sizes', 'colors')
    def validate_list_fields(cls, v):
        """Валидация списков - удаляем пустые строки и дубликаты"""
        if v is not None:
            # Удаляем пустые строки
            v = [item for item in v if item and str(item).strip()]
            # Удаляем дубликаты
            v = list(dict.fromkeys(v))
        return v
    
    @field_validator('colors')
    def validate_colors(cls, v):
        """Валидация цветов"""
        valid_colors = {"black", "white", "gray", "red", "blue", "green", 
                       "yellow", "pink", "purple", "brown", "orange", 
                       "beige", "multicolor"}
        if v is not None:
            invalid = [color for color in v if color.lower() not in valid_colors]
            if invalid:
                raise ValueError(f"Недопустимые цвета: {invalid}")
        return v
    
    # Валидаторы
    @field_validator('max_price')
    def validate_price_range(cls, v, values):
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if v < values['min_price']:
                raise ValueError('max_price должен быть больше или равен min_price')
        return v
    
    # @field_validator('created_after', 'created_before')
    # def validate_date_format(cls, v):
    #     if v:
    #         try:
    #             from datetime import datetime
    #             datetime.strptime(v, '%Y-%m-%d')
    #         except ValueError:
    #             raise ValueError('Дата должна быть в формате YYYY-MM-DD')
    #     return v
    
    def get_skip(self):
        """Вычисляет offset для пагинации"""
        return (self.page - 1) * self.per_page
    
    def get_limit(self):
        """Возвращает limit для пагинации"""
        return self.per_page
    
    def get_sort_by(self):
        """Возвращает параметры сортировки"""
        if self.sorting:
            if self.sorting.sort:
                return self.sorting.sort.get_sort_expressions()
            elif self.sorting.sort_by:
                # Упрощенная сортировка
                sort_mapping = {
                    SortBy.NEWEST: "created_at DESC",
                    SortBy.OLDEST: "created_at ASC",
                    SortBy.PRICE_ASC: "price ASC",
                    SortBy.PRICE_DESC: "price DESC",
                    SortBy.POPULAR: "((view_count * 0.5) + (favorite_count * 0.5)) DESC",
                }
                return [sort_mapping.get(self.sorting.sort_by, "created_at DESC")]
        
        # Сортировка по умолчанию
        return ["created_at DESC"]
    
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

class ImageOrderUpdate(BaseModel):
    image_ids: list[int] = Field(..., min_items=1, description="Список ID изображений в новом порядке")