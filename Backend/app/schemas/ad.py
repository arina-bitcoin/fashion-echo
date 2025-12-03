from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AdType(str, Enum):
    SELL = "sell"
    EXCHANGE = "exchange"
    BUY_REQUEST = "buy_request"

class AdCondition(str, Enum):
    NEW = "new"
    LIKE_NEW = "like_new"
    EXCELLENT = "excellent"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_REPAIR = "needs_repair"

class AdBase(BaseModel):
    type: AdType
    title: str
    description: Optional[str] = None
    price: Optional[float] = None
    condition: str
    main_categories: Optional[List[str]] = []  # men, women, kids, unisex, baby
    subcategories: Optional[List[str]] = []  # formal, casual, sports, outerwear, underwear, swimwear, accessories, shoes, bags, jewelry
    seasons: Optional[List[str]] = []  # winter, spring, summer, autumn, all_season
    size: Optional[str] = None
    brand: Optional[str] = None
    colors: Optional[List[str]] = []
    category: Optional[str] = None  # Для обратной совместимости (deprecated)

class AdCreate(AdBase):
    images: Optional[List[str]] = []
    
    @validator('price')
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
    images: List[str] = []
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True