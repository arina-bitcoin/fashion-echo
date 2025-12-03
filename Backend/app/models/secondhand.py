from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON, DateTime, Index
from sqlalchemy.sql import func
from Backend.app.core.database import Base


class Secondhand(Base):
    __tablename__ = "secondhands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # добавляем город (в схемах он уже есть)
    city = Column(String, nullable=True, index=True)

    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    description = Column(Text)
    opening_hours = Column(JSON)  # {"mon": "10:00-20:00", ...}
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        # по координатам
        Index("idx_secondhand_location", "latitude", "longitude"),
        # активные секонды в городе
        Index("idx_secondhand_city_active", "city", "is_active"),
    )
