from pydantic import BaseModel, EmailStr, field_validator, ConfigDict, model_validator
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

    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    """
    Базовая модель пользователя.
    """
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

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
    name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(UserBase):
    """
    Обновление профиля: все поля опциональны + настройки.
    Используется в /api/users/me (PUT).
    """
    # full_name: Optional[str] = None
    # phone: Optional[str] = None
    settings: Optional[UserSettings] = None

    model_config = ConfigDict(from_attributes=True)

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

    # @model_validator(mode='before')
    # @classmethod
    # def convert_name_to_full_name(cls, data):
    #     """Конвертирует поле 'name' из БД в 'full_name' в схеме"""
    #     if isinstance(data, dict):
    #         # Если в данных есть 'name', но нет 'full_name' - копируем значение
    #         if 'name' in data and ('full_name' not in data or data['full_name'] is None):
    #             data['full_name'] = data['name']
    #         # Также сохраняем обратную совместимость: если передали full_name, сохраняем в name
    #         if 'full_name' in data and ('name' not in data or data['name'] is None):
    #             data['name'] = data['full_name']
    #     elif hasattr(data, 'name'):
    #         # Для объектов SQLAlchemy
    #         if not hasattr(data, 'full_name') or data.full_name is None:
    #             data.full_name = data.name
    #         if data.name is None and hasattr(data, 'full_name'):
    #             data.name = data.full_name
    #     return data

    model_config = ConfigDict(from_attributes=True)

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
    
    model_config = ConfigDict(from_attributes=True)

class UserWithAvatarResponse(UserResponse):
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class UserPublicInfo(BaseModel):
    """Публичная информация о пользователе для отображения контактов продавца"""
    id: int
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    # @model_validator(mode='before')
    # @classmethod
    # def convert_name_to_full_name(cls, data):
    #     if isinstance(data, dict):
    #         if 'name' in data and ('full_name' not in data or data['full_name'] is None):
    #             data['full_name'] = data['name']
    #         if 'full_name' in data and ('name' not in data or data['name'] is None):
    #             data['name'] = data['full_name']
    #     elif hasattr(data, 'name'):
    #         if not hasattr(data, 'full_name') or data.full_name is None:
    #             data.full_name = data.name
    #         if data.name is None and hasattr(data, 'full_name'):
    #             data.name = data.full_name
    #     return data
    
    model_config = ConfigDict(from_attributes=True)
