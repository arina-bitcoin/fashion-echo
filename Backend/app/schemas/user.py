from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserSettings(BaseModel):
    """
    Настройки пользователя
    """
    notifications: bool = True
    theme: str = "light"
    language: str = "ru"
    email_notifications: bool = True

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(BaseModel):
    """
    Схема для регистрации пользователя.
    Ровно то, что шлёт тест:
    - email (обязательно)
    - password (обязательно)
    - full_name (опционально)
    - phone (опционально)
    """
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(UserBase):
    """
    Обновление профиля: все поля опциональны + настройки.
    """
    settings: Optional[UserSettings] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    settings: Optional[UserSettings] = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    def new_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v
