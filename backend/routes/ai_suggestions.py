from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas.ai_suggestion import (
    AISuggestionCreate, 
    AISuggestionResponse, 
    AISuggestionRequest,
    AISuggestionUpdate
)
from services.ai_suggestion import AISuggestionService
from models_init import User
from config import settings

router = APIRouter()


@router.post("/test-generate")
async def test_generate_suggestion(request: dict):
    try:
        from services.ai_service import ai_service
        
        context = request.get('context', '')
        inline_mode = request.get('inline_mode', False)
        style = request.get('style', 'neutral')
        max_length = request.get('max_length', 150 if not inline_mode else 50)
        chapter_id = request.get('chapter_id')
        
        # Выбираем правильный метод в зависимости от режима
        if inline_mode:
            continuation = await ai_service.generate_inline_continuation(
                context=context,
                style=style,
                chapter_id=chapter_id,
                use_full_context=True
            )
        else:
            continuation = await ai_service.generate_suggestion_continuation(
                context=context,
                style=style,
                max_length=max_length,
                chapter_id=chapter_id,
                use_full_context=True
            )
        
        return {
            "content": continuation,
            "suggestion_type": request.get('suggestion_type', 'text_completion'),
            "model_used": "gpt-4o-mini",
            "inline_mode": inline_mode,
            "success": True
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating test suggestion: {str(e)}"
        )


@router.post("/inline-suggestion")
async def generate_inline_suggestion(
    request: dict,
    db: Session = Depends(get_db)
):

    try:
        context = request.get('context', '')
        chapter_id = request.get('chapter_id')
        
        if not context or len(context) < 10:
            return {"content": "", "success": False}
        
        # Используем новый специализированный метод для inline подсказок
        from services.ai_service import ai_service
        
        continuation = await ai_service.generate_inline_continuation(
            context=context,
            style='neutral',
            chapter_id=chapter_id,
            use_full_context=True
        )
        
        return {
            "content": continuation.strip(),
            "model_used": "gpt-4o-mini",
            "inline_mode": True,
            "success": True
        }
            
    except Exception as e:
        return {"content": "", "success": False, "error": str(e)}

# Простой health check для AI
@router.get("/health")
async def ai_health():
    """Проверка состояния AI сервиса."""
    try:
        from services.ai_service import SmartAIService
        ai_service = SmartAIService()
        return {
            "status": "healthy",
            "openai_configured": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here"),
            "api_key_set": bool(settings.OPENAI_API_KEY),
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "openai_configured": False
        }

# Роуты с авторизацией (для полной версии)
@router.post("/generate", response_model=AISuggestionResponse)
async def generate_suggestion(
    request: AISuggestionRequest,
    db: Session = Depends(get_db)
):
    """
    Генерация AI предложения с сохранением в БД.
    В режиме разработки создает тестового пользователя автоматически.
    """
    try:
        # Создаем или получаем тестового пользователя
        test_user = db.query(User).filter(User.username == "test_user").first()
        
        if not test_user:
            from services.auth import AuthService
            test_user = User(
                username="test_user",
                email="test@example.com", 
                hashed_password=AuthService.get_password_hash("test123"),
                is_active=True,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
        
        return await AISuggestionService.generate_suggestion(db, request, test_user.id)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating suggestion: {str(e)}"
        )

@router.get("/", response_model=List[AISuggestionResponse])
async def get_suggestions(
    novel_id: Optional[int] = None,
    chapter_id: Optional[int] = None,
    suggestion_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Получение списка AI предложений."""
    # Получаем тестового пользователя
    test_user = db.query(User).filter(User.username == "test_user").first()
    if not test_user:
        return []
    
    return AISuggestionService.get_suggestions(
        db, test_user.id, novel_id, chapter_id, suggestion_type, skip, limit
    )