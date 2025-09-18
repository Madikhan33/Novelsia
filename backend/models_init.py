"""
Модуль для правильной инициализации всех моделей SQLAlchemy.
Импортирует все модели в правильном порядке для избежания конфликтов мапперов.
"""

# Импортируем базу данных
from database import Base

# Импортируем все модели в правильном порядке
from models.user import User
from models.novel import Novel  
from models.chapter import Chapter
from models.ai_suggestion import AISuggestion

# Экспортируем все модели
__all__ = ['User', 'Novel', 'Chapter', 'AISuggestion', 'Base']