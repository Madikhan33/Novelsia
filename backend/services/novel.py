from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List, Union
from fastapi import HTTPException, status

from models_init import Novel, User, Chapter
from schemas.novel import NovelCreate, NovelUpdate
from schemas.chapter import ChapterResponse

class NovelService:
    """
    Сервис для работы с новеллами.
    """
    
    @staticmethod
    def create_novel(db: Session, novel_data: NovelCreate, author_id: int) -> Novel:
        db_novel = Novel(**novel_data.model_dump(), author_id=author_id)
        db.add(db_novel)
        db.commit()
        db.refresh(db_novel)
        return db_novel
    
    @staticmethod
    def get_novel_by_id(db: Session, novel_id: Union[int, str]) -> Optional[Novel]:
        # Преобразуем в int если передана строка
        try:
            parsed_id = int(novel_id)
        except (ValueError, TypeError):
            return None
        return db.query(Novel).filter(Novel.id == parsed_id).first()
    
    @staticmethod
    def get_novels(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        genre: Optional[str] = None,
        status: Optional[str] = None,
        is_public: Optional[bool] = None,
        author_id: Optional[int] = None
    ) -> List[Novel]:
        query = NovelService._get_novel_query(db, genre, status, is_public, author_id)
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def _get_novel_query(
        db: Session,
        genre: Optional[str] = None,
        status: Optional[str] = None,
        is_public: Optional[bool] = None,
        author_id: Optional[int] = None
    ):
        """Вспомогательный метод для построения запроса к новеллам с фильтрами"""
        query = db.query(Novel)
        if genre: 
            query = query.filter(Novel.genre == genre)
        if status: 
            query = query.filter(Novel.status == status)
        if is_public is not None: 
            query = query.filter(Novel.is_public == is_public)
        if author_id: 
            query = query.filter(Novel.author_id == author_id)
        return query
    
    @staticmethod
    def update_novel(
        db: Session, 
        novel_id: int, 
        novel_data: NovelUpdate
    ) -> Optional[Novel]:
        db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not db_novel: return None
        for key, value in novel_data.model_dump(exclude_unset=True).items():
            setattr(db_novel, key, value)
        db.commit()
        db.refresh(db_novel)
        return db_novel
    
    @staticmethod
    def delete_novel(db: Session, novel_id: int) -> bool:
        db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not db_novel: return False
        db.delete(db_novel)
        db.commit()
        return True
    
    @staticmethod
    def get_novel_chapters(db: Session, novel_id: int) -> List[Chapter]:
        novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not novel: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
        return list(novel.chapters)
    
    @staticmethod
    def import_novel_from_file(db: Session, file_content: dict, author_id: int) -> Novel:
        novel_title = file_content.get("bookTitle", "Imported Novel")
        chapters_data = file_content.get("chapters", [])

        # Create the novel
        novel_create_data = NovelCreate(title=novel_title)
        db_novel = NovelService.create_novel(db, novel_create_data, author_id)

        # Import chapters for the new novel
        from services.chapter import ChapterService # Avoid circular import
        for chapter_data in chapters_data:
            chapter_data['novel_id'] = db_novel.id # Link chapter to the new novel
            ChapterService.create_chapter(db, chapter_data) # Assuming create_chapter can take dict

        return db_novel
    
    @staticmethod
    def publish_novel(db: Session, novel_id: int) -> bool:
        """
        Публикация новеллы.
        """
        db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not db.novel: return False
        db_novel.is_public = True
        db.commit()
        db.refresh(db_novel)
        return True
    
    
    @staticmethod
    def get_novel_stats(db: Session, novel_id: int) -> dict:
        """
        Получение статистики новеллы.
        """
        db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not db_novel: return None
        return {
            "total_words": sum(len(chapter.content.split()) for chapter in db_novel.chapters),
            "total_chapters": len(db_novel.chapters),
            "reading_time": sum(len(chapter.content.split()) for chapter in db_novel.chapters) / 200,
        }
    
    @staticmethod
    def check_author_permission(db: Session, novel_id: int, user_id: int) -> bool:
        """
        Проверка прав автора на новеллу.
        """
        db_novel = db.query(Novel).filter(Novel.id == novel_id).first()
        if not db_novel: return False
        return db_novel.author_id == user_id
    
    @staticmethod
    def get_public_novels(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        genre: Optional[str] = None
    ) -> List[Novel]:
        """
        Получение публичных новелл.
        """
        db_novels = db.query(Novel).filter(Novel.is_public == True)
        if genre: db_novels = db_novels.filter(Novel.genre == genre)
        return db_novels.offset(skip).limit(limit).all()

    
    @staticmethod
    def search_novels(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Novel]:
        """
        Поиск новелл по тексту.
        """

        db_find_novels = db.query(Novel).filter(Novel.is_public == True)
        if query: db_find_novels = db_find_novels.filter(Novel.title.ilike(f"%{query}%") | Novel.description.ilike(f"%{query}%"))
        return db_find_novels.offset(skip).limit(limit).all()
    