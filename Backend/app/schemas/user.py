<<<<<<< HEAD
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
=======
from pydantic import BaseModel, EmailStr, field_validator
>>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
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
<<<<<<< HEAD
    name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    name: str
=======
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
>>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
    email: EmailStr
    phone: str
    password: str
<<<<<<< HEAD
    
=======
    full_name: Optional[str] = None
    phone: Optional[str] = None

>>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(UserBase):
<<<<<<< HEAD
    phone: Optional[str] = None
=======
    """
    Обновление профиля: все поля опциональны + настройки.
    """
    settings: Optional[UserSettings] = None

>>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_verified: bool
    avatar: Optional[str] = None
    created_at: datetime
<<<<<<< HEAD
    last_login: Optional[datetime] = None
    
    # class Config:
    #     from_attributes = True
=======
    settings: Optional[UserSettings] = None

    class Config:
        from_attributes = True
>>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator('new_password')
    def new_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v
<<<<<<< HEAD
    
class UserWithAvatarResponse(UserResponse):
    avatar_url: Optional[str] = None
=======
>>>>>>> fa5e3c9a53d1ee55e894efa86eb81844d1f858db
