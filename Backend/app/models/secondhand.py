from sqlalchemy import Column, Integer, String, Float, Boolean, Text, JSON
from Backend.app.core.database import Base

class Secondhand(Base):
    __tablename__ = "secondhands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String)
    email = Column(String)
    website = Column(String)
    description = Column(Text)
    opening_hours = Column(JSON)  # {"monday": "10:00-20:00", ...}
    is_active = Column(Boolean, default=True)