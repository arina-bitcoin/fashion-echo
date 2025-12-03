from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class UserSettings(BaseModel):
    """
    Настройки пользователя.
    """
    notifications: bool = True         # пуш/внутренние уведомления
    theme: str = "light"               # "light" | "dark"
    language: str = "ru"               # язык интерфейса
    email_notifications: bool = True   # слать ли уведомления на email


class UserBase(BaseModel):
    """
    Базовая модель пользователя.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(BaseModel):
    """
    Схема для регистрации пользователя.
    - email (обязательно)
    - password (обязательно)
    - full_name (опционально)
    - phone (опционально)
    """
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v


class UserUpdate(UserBase):
    """
    Обновление профиля: все поля опциональны + настройки.
    Используется в /api/users/me (PUT).
    """
    full_name: Optional[str] = None
    phone: Optional[str] = None
    settings: Optional[UserSettings] = None


class UserResponse(UserBase):
    """
    Ответ с информацией о пользователе.
    Используется как response_model в /auth/register, /users/me и др.
    """
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    settings: Optional[UserSettings] = None

    @property
    def full_name(self) -> Optional[str]:
        return self.name  # Или vice versa, в зависимости от того, что использует ваша БД

class ChangePasswordRequest(BaseModel):
    """
    Тело запроса для смены пароля /users/change-password.
    """
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def new_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("New password must be at least 8 characters long")
        return v
    
class UserWithAvatarResponse(UserResponse):
    avatar_url: Optional[str] = None

class UserPublicInfo(BaseModel):
    """Публичная информация о пользователе для отображения контактов продавца"""
    id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)
