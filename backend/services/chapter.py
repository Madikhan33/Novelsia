from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List, Union
from fastapi import HTTPException, status
import re

from models_init import Chapter, Novel
from schemas.chapter import ChapterCreate, ChapterUpdate

class ChapterService:
    """
    Сервис для работы с главами.
    """
    
    @staticmethod
    def calculate_word_count(text: str) -> int:
        if not text: return 0
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)
    
    @staticmethod
    def calculate_reading_time(word_count: int, words_per_minute: int = 200) -> float:
        if word_count == 0: return 0.0
        return round(word_count / words_per_minute, 2)
    
    @staticmethod
    def get_next_chapter_number(db: Session, novel_id: int) -> int:
        max_chapter = db.query(func.max(Chapter.chapter_number)).filter(Chapter.novel_id == novel_id).scalar()
        return (max_chapter or 0) + 1

    @staticmethod
    def create_chapter(
        db: Session, 
        chapter_data: ChapterCreate, 
        # author_id: int # Removed author_id, as chapter is tied to novel
    ) -> Chapter:
        novel = db.query(Novel).filter(Novel.id == chapter_data.novel_id).first()
        if not novel: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")

        word_count = ChapterService.calculate_word_count(chapter_data.content)
        reading_time = ChapterService.calculate_reading_time(word_count)
        chapter_number = chapter_data.chapter_number or ChapterService.get_next_chapter_number(db, chapter_data.novel_id)

        db_chapter = Chapter(
            **chapter_data.model_dump(exclude_unset=True),
            word_count=word_count,
            reading_time=reading_time,
            chapter_number=chapter_number
        )
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter
    
    @staticmethod
    def get_chapter_by_id(db: Session, chapter_id: int) -> Optional[Chapter]:
        return db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    @staticmethod
    def get_chapters(
        db: Session,
        novel_id: Optional[Union[int, str]] = None,
        skip: int = 0,
        limit: int = 100,
        is_published: Optional[bool] = None
    ) -> List[Chapter]:
        query = db.query(Chapter)
        if novel_id: query = query.filter(Chapter.novel_id == novel_id)
        if is_published is not None: query = query.filter(Chapter.is_published == is_published)
        return query.order_by(Chapter.chapter_number).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_chapter(
        db: Session, 
        chapter_id: int, 
        chapter_data: ChapterUpdate
    ) -> Optional[Chapter]:
        db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not db_chapter: return None

        update_data = chapter_data.model_dump(exclude_unset=True)
        
        if "content" in update_data: # Recalculate word count and reading time if content changes
            word_count = ChapterService.calculate_word_count(update_data["content"])
            reading_time = ChapterService.calculate_reading_time(word_count)
            update_data['word_count'] = word_count
            update_data['reading_time'] = reading_time

        for key, value in update_data.items():
            setattr(db_chapter, key, value)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter
    
    @staticmethod
    def delete_chapter(db: Session, chapter_id: int) -> bool:
        db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not db_chapter: return False
        db.delete(db_chapter)
        db.commit()
        return True
    
    @staticmethod
    def publish_chapter(db: Session, chapter_id: int) -> bool:
        """
        Публикация главы.
        """
        db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not db_chapter: return False
        db_chapter.is_published = True
        db.commit()
        db.refresh(db_chapter)
        return True
    
    @staticmethod
    def reorder_chapters(
        db: Session, 
        chapter_id: int, 
        new_position: int
    ) -> bool:
        """
        Изменение порядка глав.
        """
        db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not db_chapter: return False
        db_chapter.chapter_number = new_position
        db.commit()
        db.refresh(db_chapter)
        return True
    
    @staticmethod
    def get_chapter_stats(db: Session, chapter_id: int) -> dict:
        """
        Получение статистики главы.
        """
        db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not db_chapter: return None
        return {
            "word_count": db_chapter.word_count,
            "reading_time": db_chapter.reading_time,
            "views": db_chapter.views
        }
    
    @staticmethod
    def increment_views(db: Session, chapter_id: int) -> bool:
        """
        Увеличение счетчика просмотров.
        """
        db_chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not db_chapter: return False
        db.chapter.views += 1
        db.commit()
        db.refresh(db_chapter)
        return True
        
