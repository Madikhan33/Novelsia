from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List
from fastapi import HTTPException, status
from openai import AsyncOpenAI
from config import settings

from models_init import AISuggestion, Chapter, Novel
from schemas.ai_suggestion import AISuggestionCreate, AISuggestionRequest

class AISuggestionService:

    def __init__(self):
   
        try:
            if settings.OPENAI_API_KEY:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            else:
                self.client = None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to initialize OpenAI client: {str(e)}")
    
    @staticmethod
    def create_suggestion(
        db: Session, 
        suggestion_data: AISuggestionCreate
    ) -> AISuggestion:
        """Создание AI предложения в БД."""
        db_suggestion = AISuggestion(**suggestion_data.model_dump())
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    
    @staticmethod
    def get_suggestions(
        db: Session,
        user_id: int,
        novel_id: Optional[int] = None,
        chapter_id: Optional[int] = None,
        suggestion_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AISuggestion]:
        """Получение списка AI предложений."""
        query = db.query(AISuggestion).filter(AISuggestion.user_id == user_id)
        
        if novel_id:
            query = query.filter(AISuggestion.novel_id == novel_id)
        if chapter_id:
            query = query.filter(AISuggestion.chapter_id == chapter_id)
        if suggestion_type:
            query = query.filter(AISuggestion.suggestion_type == suggestion_type)
            
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def update_suggestion(
        db: Session, 
        suggestion_id: int, 
        is_used: Optional[bool] = None,
        rating: Optional[int] = None
    ) -> Optional[AISuggestion]:
        """Обновление AI предложения."""
        db_suggestion = db.query(AISuggestion).filter(AISuggestion.id == suggestion_id).first()
        if not db_suggestion:
            return None
            
        if is_used is not None:
            db_suggestion.is_used = is_used
        if rating is not None:
            db_suggestion.rating = rating
            
        db.commit()
        db.refresh(db_suggestion)
        return db_suggestion
    
    @staticmethod
    def delete_suggestion(db: Session, suggestion_id: int) -> bool:
        """Удаление AI предложения."""
        db_suggestion = db.query(AISuggestion).filter(AISuggestion.id == suggestion_id).first()
        if not db_suggestion:
            return False
            
        db.delete(db_suggestion)
        db.commit()
        return True
    
    @staticmethod
    async def generate_suggestion(
        db: Session,
        request: AISuggestionRequest, 
        user_id: int
    ) -> AISuggestion:
        """
        Генерация AI предложения с использованием улучшенного AI сервиса.
        """
        try:
            # Импортируем здесь чтобы избежать циклических импортов
            from .ai_service import ai_service
            
            # Генерируем умные предложения
            suggestions = await ai_service.generate_smart_suggestions(db, request, user_id)
            
            if not suggestions:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate suggestions"
                )
            
            # Берем первое (лучшее) предложение
            best_suggestion = suggestions[0]
            
            # Сохраняем в базу данных
            db_suggestion = await ai_service.save_suggestion(
                db, best_suggestion, request, user_id, tokens_used=len(best_suggestion.split())
            )
            
            return db_suggestion
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating suggestion: {str(e)}"
            )
    
    @staticmethod
    def get_suggestion_by_id(db: Session, suggestion_id: int) -> Optional[AISuggestion]:
        """Получение AI предложения по ID."""
        return db.query(AISuggestion).filter(AISuggestion.id == suggestion_id).first()