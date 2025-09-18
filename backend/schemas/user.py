from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

class UserBase(BaseModel):
    """
    Базовая схема пользователя.
    Содержит общие поля для создания и обновления.
    """
    username: str
    email: EmailStr

class UserCreate(UserBase):
    """
    Схема для создания пользователя.
    Добавляет поле password для регистрации.
    """
    password: str = Field(..., min_length=6, max_length=128)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        if len(v) > 128:
            raise ValueError('Пароль слишком длинный')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Имя пользователя должно содержать минимум 3 символа')
        if len(v) > 50:
            raise ValueError('Имя пользователя слишком длинное')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Имя пользователя может содержать только буквы, цифры, дефисы и подчеркивания')
        return v

class UserUpdate(BaseModel):
    """
    Схема для обновления пользователя.
    Все поля опциональны.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserLogin(BaseModel):
    """
    Схема для входа пользователя.
    """
    username: str  # или email
    password: str

class UserResponse(UserBase):
    """
    Схема для ответа с данными пользователя.
    Исключает пароль и добавляет системные поля.
    """
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """
    Схема для JWT токена.
    """
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """
    Схема для данных в токене.
    """
    username: Optional[str] = None 