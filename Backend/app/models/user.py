from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)  # nullable для гостевого доступа
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    "ХЗ ABOUT THAT"
    # phone = Column(String(20), nullable=True)
    avatar = Column(String(200), nullable=True)  # путь к аватару
    settings = Column(JSON)  # {'notifications': True, 'theme': 'light'}
    last_login = Column(DateTime, nullable=True)

    ads = relationship("Ad", back_populates="user")
    favorite_ads = relationship("FavoriteAd", back_populates="user")
    
# from sqlalchemy import Boolean, String
# from sqlalchemy.orm import Mapped, mapped_column
# from app.database import Base, int_pk, email_type, str_null_true, created_at, updated_at

# class User(Base):
#     """Модель пользователя для SQLite"""
    
#     id: Mapped[int_pk]
#     email: Mapped[email_type]  # String(255) с индексом
#     hashed_password: Mapped[str] = mapped_column(String(255), nullable=True)
#     full_name: Mapped[str_null_true]
#     phone: Mapped[str_null_true]
    
#     # Статусы пользователя
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)
#     is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
#     # Наследуем автоматические timestamp поля из Base
#     # created_at: Mapped[created_at] - уже есть в Base
#     # updated_at: Mapped[updated_at] - уже есть в Base
    
#     def __repr__(self):
#         return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"