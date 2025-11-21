# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime

# class UserBase(BaseModel):
#     email: Optional[EmailStr] = None
#     full_name: Optional[str] = None
#     phone: Optional[str] = None

# class UserCreate(UserBase):
#     password: str

# class UserUpdate(UserBase):
#     pass

# class UserResponse(UserBase):
#     id: int
#     is_active: bool
#     created_at: datetime
    
#     class Config:
#         from_attributes = True

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    name: str
    
    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class UserUpdate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
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