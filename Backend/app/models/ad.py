from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Text, 
    Float, 
    Boolean, 
    DateTime, 
    ForeignKey, 
    JSON,
    Numeric,
    UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from Backend.app.core.database import Base
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLEnum
from enum import Enum as PyEnum

# Enum для статуса товара
class Condition(str, PyEnum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_REPAIR = "needs_repair"

# Enum для сезонов
class Season(str, PyEnum):
    WINTER = "winter"
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    ALL_SEASON = "all_season"

# Enum для основных категорий
class MainCategory(str, PyEnum):
    MEN = "men"
    WOMEN = "women"
    KIDS = "kids"
    UNISEX = "unisex"
    BABY = "baby"

# Enum для подкатегорий
class SubCategory(str, PyEnum):
    FORMAL = "formal"
    CASUAL = "casual"
    SPORTS = "sports"
    OUTERWEAR = "outerwear"
    UNDERWEAR = "underwear"
    SWIMWEAR = "swimwear"
    ACCESSORIES = "accessories"
    SHOES = "shoes"
    BAGS = "bags"
    JEWELRY = "jewelry"

class Ad(Base):
    __tablename__ = "ads"
    
    # Существующие поля
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    type = Column(String(20), nullable=False)  # sell, buy, exchange
    
    # Новые поля для фильтрации
    is_active = Column(Boolean, default=True)
    
    # Категории
    main_category = Column(SQLEnum(MainCategory), nullable=True)
    sub_category = Column(SQLEnum(SubCategory), nullable=True)
    season = Column(SQLEnum(Season), nullable=True)
    
    # Состояние товара
    condition = Column(SQLEnum(Condition), nullable=True)
    
    # Размеры (храним как строку, можно парсить)
    size = Column(String(50), nullable=True)  # "M", "42", "XS-XL"
    
    # Цвета (храним как JSON массив)
    colors = Column(JSON, nullable=True, default=list)  # ["black", "white"]
    
    # Теги для улучшенного поиска
    tags = Column(Text, nullable=True)
    
    # Статистика
    view_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    
    # Остальные поля
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    # Связи
    images = relationship("AdImage", back_populates="ad", cascade="all, delete-orphan")
    user = relationship("User", back_populates="ads")
    favorited_by = relationship("User", secondary="favorite_ads", back_populates="favorites")

class FavoriteAd(Base):
    __tablename__ = "favorite_ads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    ad_id = Column(Integer, ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Уникальный constraint для предотвращения дубликатов
    __table_args__ = (
        (UniqueConstraint('user_id', 'ad_id', name='unique_user_ad')),
    )
    
    # Связи
    user = relationship("User", back_populates="favorite_ads")
    ad = relationship("Ad", back_populates="favorited_by_users")


# Таблица для изображений объявлений
class AdImage(Base):
    __tablename__ = "ad_images"
    
    id = Column(Integer, primary_key=True, index=True)
    ad_id = Column(Integer, ForeignKey("ads.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    order = Column(Integer, default=0)
    is_main = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связь
    ad = relationship("Ad", back_populates="images")