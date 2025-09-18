"""
Пользовательские исключения для приложения.
"""

from fastapi import HTTPException, status

class NovelsiaException(HTTPException):
    """
    Базовое исключение для приложения.
    """
    pass

class UserNotFoundException(NovelsiaException):
    """
    Исключение при отсутствии пользователя.
    """
    def __init__(self, user_id: int = None, username: str = None):
        detail = f"Пользователь не найден"
        if user_id:
            detail = f"Пользователь с ID {user_id} не найден"
        elif username:
            detail = f"Пользователь '{username}' не найден"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class NovelNotFoundException(NovelsiaException):
    """
    Исключение при отсутствии новеллы.
    """
    def __init__(self, novel_id: int):
        detail = f"Новелла с ID {novel_id} не найдена"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ChapterNotFoundException(NovelsiaException):
    """
    Исключение при отсутствии главы.
    """
    def __init__(self, chapter_id: int):
        detail = f"Глава с ID {chapter_id} не найдена"
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class PermissionDeniedException(NovelsiaException):
    """
    Исключение при отсутствии прав доступа.
    """
    def __init__(self, message: str = "Недостаточно прав для выполнения операции"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)

class InvalidCredentialsException(NovelsiaException):
    """
    Исключение при неверных учетных данных.
    """
    def __init__(self, message: str = "Неверные учетные данные"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)

class DuplicateUserException(NovelsiaException):
    """
    Исключение при дублировании пользователя.
    """
    def __init__(self, field: str, value: str):
        detail = f"Пользователь с {field} '{value}' уже существует"
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class AIException(NovelsiaException):
    """
    Исключение при ошибках AI сервиса.
    """
    def __init__(self, message: str = "Ошибка AI сервиса"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=message)

class ValidationException(NovelsiaException):
    """
    Исключение при ошибках валидации.
    """
    def __init__(self, message: str = "Ошибка валидации данных"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message) 