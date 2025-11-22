from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    name: str
    email: EmailStr
    phone: str
    password: str
    
    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(UserBase):
    phone: Optional[str] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_verified: bool
    avatar: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    # class Config:
    #     from_attributes = True

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @field_validator('new_password')
    def new_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters long')
        return v
    
class UserWithAvatarResponse(UserResponse):
    avatar_url: Optional[str] = None