from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models_init import User

# Настройка для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")
class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def create_reset_token(user_id: int) -> str:
        """Создание токена для сброса пароля"""
        to_encode = {"sub": str(user_id), "type": "reset"}
        expire = datetime.now(timezone.utc) + timedelta(hours=1)  # Токен действует 1 час
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_reset_token(token: str) -> Optional[dict]:
        """Проверка токена сброса пароля"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get("type") != "reset":
                return None
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:

        user = db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        if not user or not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Attempting to validate token: {token[:20]}...")
        payload = AuthService.verify_token(token)
        if not payload:
            logger.error("Token verification failed")
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        user_id = payload.get("sub")
        logger.info(f"Extracted user_id from token: {user_id}")
        if not user_id:
            logger.error("No user_id in token payload")
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        
        # Преобразуем user_id в int, если он строка
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid user_id format: {user_id}")
            raise HTTPException(status_code=401, detail="Invalid token format")
        
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            logger.error(f"User not found in database: {user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        
        logger.info(f"User authenticated successfully: {db_user.username}")
        return db_user
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:

    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user