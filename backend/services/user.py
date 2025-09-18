from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from fastapi import HTTPException, status
import logging

from models_init import User
from schemas.user import UserCreate, UserUpdate
from services.auth import AuthService
from models_init import Novel

logger = logging.getLogger(__name__)

class UserService:
    """
    Сервис для работы с пользователями.
    """
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Создание нового пользователя.
        """
        try:
            logger.info(f"Attempting to create user with username: {user_data.username}, email: {user_data.email}")
            
            # Проверяем уникальность username и email
            existing_user = db.query(User).filter(
                (User.username == user_data.username) | (User.email == user_data.email)
            ).first()
            if existing_user:
                logger.warning(f"User already exists: username={existing_user.username}, email={existing_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username or email already registered"
                )
            
            # Создаем пользователя
            db_user = User(
                username=user_data.username,
                email=user_data.email,
                hashed_password=AuthService.get_password_hash(user_data.password),
                is_active=True,
                is_verified=False,
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            
            logger.info(f"User created successfully with ID: {db_user.id}")
            return db_user
            
        except HTTPException as e:
            logger.error(f"HTTP Exception during user creation: {e.detail}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Получение пользователя по ID.
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user: return None
        return db_user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        Получение пользователя по username.
        """
        db_user = db.query(User).filter(User.username == username).first()
        if not db_user: return None
        return db_user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Получение пользователя по email.
        """
        db_user = db.query(User).filter(User.email == email).first()
        if not db_user: return None
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Обновление пользователя.
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user: return None
        for field, value in user_data.model_dump().items():
            setattr(db_user, field, value)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Удаление пользователя.
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user: return False
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def get_users(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """
        Получение списка пользователей.
        """
        db_users = db.query(User)
        if is_active: db_users = db_users.filter(User.is_active == is_active)
        return db_users.offset(skip).limit(limit).all()
    
    @staticmethod
    def verify_email(db: Session, user_id: int) -> bool:
        """
        Подтверждение email пользователя.
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user: return False
        db_user.is_verified = True
        db.commit()
        db.refresh(db_user)
        return True
    
    @staticmethod
    def change_password(
        db: Session, 
        user_id: int, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """
        Изменение пароля пользователя.
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user: return False
        if not AuthService.verify_password(current_password, db_user.hashed_password): return False
        db_user.hashed_password = AuthService.get_password_hash(new_password)
        db.commit()
        db.refresh(db_user)
        return True
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> dict:
        """
        Получение статистики пользователя.
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user: 
            return None
    
        return {
            "total_novels": 0,  # db.query(Novel).filter(Novel.author_id == user_id).count(),
            "total_chapters": 0,  # Подсчет через запросы к БД
            "total_words": 0,  # Подсчет через запросы к БД
            "total_published_works": 0,  # db.query(Novel).filter(Novel.author_id == user_id, Novel.is_public == True).count(),
        }