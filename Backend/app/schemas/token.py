from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int = None
    email: str = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# ДОБАВИТЬ эту схему
class LoginRequest(BaseModel):
    email: EmailStr
    password: str