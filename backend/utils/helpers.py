"""
Вспомогательные функции для приложения.
"""



import re
from typing import Optional
from datetime import datetime
from pydantic import EmailStr
from slugify import slugify





def validate_email(email: str) -> bool:
    try:
        EmailStr(email)
        return True
    except ValueError:
        return False
    



    

def validate_password(password: str) -> bool:
    """
    Валидация пароля.
    """
    uniq_chars = ['*', '!', '@', '#', '$', '%', '^', '&', '(', ')', '_', '+', '=', '-', '/', '?', '|', '\\', '~', '`', '{', '}', '[', ']', ':', ';', '"', "'", '<', '>', ',', '.', ' ']
    if password[0].islower():
        return False
    if len(password) < 8:
        return False
    if password not in uniq_chars:
        return False
    return True



    

def calculate_reading_time(text: str, words_per_second: int = 60) -> float:
    """
    Расчет времени чтения текста.
    
    """

    words_length = len(text.split())
    reading_time = words_length / words_per_second * 60
    result = f"{reading_time:.2f} minutes"
    return result
    
    

    
    

def count_words(text: str) -> int:
    """
    Подсчет слов в тексте.
    """
    
    text_length = len(text.split())
    return text_length




def sanitize_filename(filename: str) -> str:
    """
    Очистка имени файла от недопустимых символов.
    
    TODO: Реализовать:
    - Удаление недопустимых символов
    - Замена пробелов на подчеркивания
    - Возврат очищенного имени
    """

    isnotvalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in isnotvalid_chars:
        filename = filename.replace(char, '')
    filename = filename.replace(' ', '_')
    return filename




    

def generate_slug(text: str) -> str:
    """
    Генерация slug из текста.
    
    TODO: Реализовать:
    - Транслитерация кириллицы
    - Приведение к нижнему регистру
    - Замена пробелов на дефисы
    - Удаление специальных символов
    - Возврат slug
    """
    
   
    slug = slugify(text, separator='_')
    return slug
        


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Форматирование даты и времени.
    
    TODO: Реализовать:
    - Форматирование datetime
    - Возврат строки
    """

    formatted_datetime = dt.strftime(format_str)
    return formatted_datetime
    

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Обрезка текста до указанной длины.
    
    TODO: Реализовать:
    - Проверку длины текста
    - Обрезку с добавлением суффикса
    - Возврат обрезанного текста
    """

    if len(text) <= max_length:
        return text
    
    return text[:max_length] + suffix







