from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChapterBase(BaseModel):
    """
    Базовая схема главы.
    Содержит общие поля для создания и обновления.
    """
    title: str
    content: str
    chapter_number: int

class ChapterCreate(ChapterBase):
    """
    Схема для создания главы.
    """
    novel_id: int

class ChapterUpdate(BaseModel):
    """
    Схема для обновления главы.
    Все поля опциональны.
    """
    title: Optional[str] = None
    content: Optional[str] = None
    chapter_number: Optional[int] = None
    is_published: Optional[bool] = None

class ChapterResponse(ChapterBase):
    """
    Схема для ответа с данными главы.
    Добавляет системные поля и метаданные.
    """
    id: int
    novel_id: int
    word_count: int
    reading_time: float  # в минутах
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_published: bool
    views_count: int

    class Config:
        from_attributes = True

class ChapterListResponse(BaseModel):
    """
    Схема для списка глав.
    """
    chapters: list[ChapterResponse]
    total: int
    page: int
    per_page: int 