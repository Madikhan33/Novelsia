from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AISuggestionBase(BaseModel):
    """
    Базовая схема AI предложения.
    """
    suggestion_type: str  # continuation, plot_idea, character_development, etc.
    content: str
    context: Optional[str] = None

class AISuggestionCreate(AISuggestionBase):
    """
    Схема для создания AI предложения.
    """
    chapter_id: Optional[int] = None
    novel_id: Optional[int] = None
    user_id: int

class AISuggestionUpdate(BaseModel):
    """
    Схема для обновления AI предложения.
    """
    is_used: Optional[bool] = None
    rating: Optional[int] = None # 1-5

class AISuggestionResponse(AISuggestionBase):
    """
    Схема для ответа с данными AI предложения.
    """
    id: int
    chapter_id: Optional[int] = None
    novel_id: Optional[int] = None
    user_id: int
    is_used: bool
    rating: Optional[int] = None
    created_at: datetime
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None

    class Config:
        from_attributes = True

class AISuggestionRequest(BaseModel):
    """
    Схема для запроса AI предложения.
    """
    suggestion_type: str
    context: str
    chapter_id: Optional[int] = None
    novel_id: Optional[int] = None
    max_length: Optional[int] = 200  # максимальная длина предложения
    style: Optional[str] = None  # стиль написания 