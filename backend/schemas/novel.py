from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NovelBase(BaseModel):
    """
    Базовая схема новеллы.
    Содержит общие поля для создания и обновления.
    """
    title: str
    description: Optional[str] = None
    genre: Optional[str] = None
    is_public: bool = False

class NovelCreate(NovelBase):
    """
    Схема для создания новеллы.
    """
    pass

class NovelUpdate(BaseModel):
    """
    Схема для обновления новеллы.
    Все поля опциональны.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    genre: Optional[str] = None
    status: Optional[str] = None  # draft, published, completed
    is_public: Optional[bool] = None
    cover_image_url: Optional[str] = None

class NovelResponse(NovelBase):
    """
    Схема для ответа с данными новеллы.
    Добавляет системные поля и информацию об авторе.
    """
    id: int
    status: str
    cover_image_url: Optional[str] = None
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    word_count: int
    rating: Optional[int] = None
    chapters_count: Optional[int] = None  # количество глав

    class Config:
        from_attributes = True

class NovelListResponse(BaseModel):
    """
    Схема для списка новелл.
    """
    novels: List[NovelResponse]
    total: int
    page: int
    per_page: int 