# from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Float, JSON, ForeignKey
# from sqlalchemy.sql import func
# from Backend.app.core.database import Base

# class Ad(Base):
#     __tablename__ = "ads"
#     id = Column(Integer, primary_key=True, index=True)
#     type = Column(String)  # 'sell', 'exchange', 'buy'
#     title = Column(String)
#     description = Column(Text)
#     price = Column(Float, nullable=True)
#     condition = Column(String)
#     category = Column(String)
#     images = Column(JSON)  # paths to images
#     user_id = Column(Integer, ForeignKey("users.id"))
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from Backend.app.core.database import Base

class Ad(Base):
    __tablename__ = "ads"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)  # 'sell', 'exchange', 'buy_request'
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=True)  # NULL для обмена
    condition = Column(String)  # 'new', 'like_new', 'good', 'satisfactory'
    category = Column(String)   # 'clothing', 'shoes', 'accessories'
    size = Column(String)
    brand = Column(String)
    images = Column(JSON)  # Список путей к изображениям
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())