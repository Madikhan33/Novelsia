from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.user import UserUpdate, UserResponse
from services.user import UserService
from services.auth import get_current_user
from models_init import User, Novel
from models_init import Chapter
from sqlalchemy import func
from services.auth import AuthService
router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получение информации о текущем пользователе.
    """
    return current_user
    

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление профиля текущего пользователя.
    """
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_data.username:
        db_user.username = user_data.username
    if user_data.email:
        db_user.email = user_data.email
    if user_data.bio is not None:
        db_user.bio = user_data.bio
    if user_data.avatar_url is not None:
        db_user.avatar_url = user_data.avatar_url
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/me/novels")
async def get_current_user_novels(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение новелл текущего пользователя.
    """
    novels = db.query(Novel).filter(Novel.author_id == current_user.id)
    if status:
        novels = novels.filter(Novel.status == status)
    total = novels.count()
    novels = novels.offset(skip).limit(limit).all()
    return {"novels": novels, "total": total, "page": skip // limit + 1, "per_page": limit}

@router.get("/me/stats")
async def get_current_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение статистики текущего пользователя.
    """
    total_novels = db.query(Novel).filter(Novel.author_id == current_user.id).count()
    total_chapters = db.query(Chapter).filter(Chapter.novel_id.in_(db.query(Novel.id).filter(Novel.author_id == current_user.id))).count()
    total_words = db.query(Chapter).filter(Chapter.novel_id.in_(db.query(Novel.id).filter(Novel.author_id == current_user.id))).with_entities(func.sum(Chapter.word_count)).scalar()
    published_novels = db.query(Novel).filter(Novel.author_id == current_user.id, Novel.status == "published").count()
    average_rating = db.query(func.avg(Novel.rating)).filter(Novel.author_id == current_user.id).scalar()
    return {
        "total_novels": total_novels,
        "total_chapters": total_chapters,
        "total_words": total_words,
        "published_novels": published_novels,
        "average_rating": average_rating
    }




@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получение публичного профиля пользователя.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/{user_id}/novels")
async def get_user_public_novels(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получение публичных новелл пользователя.
    """
    novels = db.query(Novel).filter(Novel.author_id == user_id, Novel.is_public == True)
    total = novels.count()
    novels = novels.offset(skip).limit(limit).all()
    return {"novels": novels, "total": total, "page": skip // limit + 1, "per_page": limit}

@router.post("/me/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Изменение пароля текущего пользователя.
    """
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not AuthService.verify_password(current_password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    db_user.hashed_password = AuthService.get_password_hash(new_password)
    db.commit()
    db.refresh(db_user)
    return {"message": "Password changed successfully"}

@router.post("/me/upload-avatar")
async def upload_avatar(
    # file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка аватара пользователя.
    """
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.avatar_url = "https://example.com/avatar.jpg"
    db.commit()
    db.refresh(db_user)
    return {"avatar_url": db_user.avatar_url}

@router.delete("/me")
async def delete_account(
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление аккаунта пользователя.
    """
    db_user = db.query(User).filter(User.id == current_user.id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not AuthService.verify_password(password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid password")
    db.delete(db_user)
    db.commit()
    return {"message": "Account deleted successfully"}