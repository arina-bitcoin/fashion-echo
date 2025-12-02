# <<<<<<< HEAD
# from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
# =======
# from pydantic import BaseModel, EmailStr, field_validator
# >>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
# from typing import Optional
# from datetime import datetime
#
# class UserSettings(BaseModel):
#     """
#     Настройки пользователя
#     """
#     notifications: bool = True
#     theme: str = "light"
#     language: str = "ru"
#     email_notifications: bool = True
#
# class UserBase(BaseModel):
#     email: Optional[EmailStr] = None
# <<<<<<< HEAD
#     name: Optional[str] = None
#     phone: Optional[str] = None
#
# class UserCreate(UserBase):
#     name: str
# =======
#     full_name: Optional[str] = None
#     phone: Optional[str] = None
#
#
# class UserCreate(BaseModel):
#     """
#     Схема для регистрации пользователя.
#     Ровно то, что шлёт тест:
#     - email (обязательно)
#     - password (обязательно)
#     - full_name (опционально)
#     - phone (опционально)
#     """
# >>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
#     email: EmailStr
#     phone: str
#     password: str
# <<<<<<< HEAD
#
# =======
#     full_name: Optional[str] = None
#     phone: Optional[str] = None
#
# >>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
#     @field_validator('password')
#     def password_strength(cls, v):
#         if len(v) < 8:
#             raise ValueError('Password must be at least 8 characters long')
#         return v
#
#
# class UserUpdate(UserBase):
# <<<<<<< HEAD
#     phone: Optional[str] = None
# =======
#     """
#     Обновление профиля: все поля опциональны + настройки.
#     """
#     settings: Optional[UserSettings] = None
#
# >>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
#
# class UserResponse(UserBase):
#     model_config = ConfigDict(from_attributes=True)
#
#     id: int
#     is_active: bool
#     is_verified: bool
#     avatar: Optional[str] = None
#     created_at: datetime
# <<<<<<< HEAD
#     last_login: Optional[datetime] = None
#
#     # class Config:
#     #     from_attributes = True
# =======
#     settings: Optional[UserSettings] = None
#
#     class Config:
#         from_attributes = True
# >>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
#
#
# class ChangePasswordRequest(BaseModel):
#     current_password: str
#     new_password: str
#
#     @field_validator('new_password')
#     def new_password_strength(cls, v):
#         if len(v) < 8:
#             raise ValueError('New password must be at least 8 characters long')
#         return v
# <<<<<<< HEAD
#
# class UserWithAvatarResponse(UserResponse):
#     avatar_url: Optional[str] = None
# =======
# >>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db



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
    full_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(BaseModel):
    """
    Модель для регистрации пользователя.

    ВАЖНО: поля должны совпадать с тем, что шлёт клиент / тесты:
    - email
    - password
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


class UserUpdate(BaseModel):
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
    settings: Optional[UserSettings] = None

    class Config:
        from_attributes = True  # для работы с ORM-моделями SQLAlchemy


class UserWithAvatarResponse(UserResponse):
    """
    Расширенная модель пользователя, если где-то нужен avatar_url.
    Эндпоинты могут её использовать как response_model.
    """
    avatar_url: Optional[str] = None


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
