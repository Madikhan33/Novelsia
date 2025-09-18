from celery import Celery
from config import settings
from services.ai_suggestion import AISuggestionService

# TODO: Настроить Celery

celery_app = Celery("novelsia", broker=settings.REDIS_URL)

@celery_app.task
def generate_ai_suggestion(suggestion_type: str, context: str, user_id: int, **kwargs):
    """
    Генерация AI предложения в фоновом режиме.
    """
    return AISuggestionService.generate_suggestion(suggestion_type, context, user_id, **kwargs)

@celery_app.task
def analyze_novel_content(novel_id: int):
    """
    Анализ содержимого новеллы.
    """
    return AISuggestionService.analyze_novel_content(novel_id)

@celery_app.task
def generate_novel_summary(novel_id: int):
    """
    Генерация краткого содержания новеллы.
    """
    return AISuggestionService.generate_novel_summary(novel_id)

@celery_app.task
def suggest_improvements(chapter_id: int):
    """
    Предложение улучшений для главы.
    """
    return AISuggestionService.suggest_improvements(chapter_id)

@celery_app.task
def generate_character_analysis(novel_id: int, character_name: str):
    """
    Анализ персонажа.
    """
    return AISuggestionService.generate_character_analysis(novel_id, character_name)