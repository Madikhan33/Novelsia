from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas.novel import NovelCreate, NovelUpdate, NovelResponse, NovelListResponse
from schemas.chapter import ChapterResponse
from services.novel import NovelService
from services.auth import get_current_user
from models_init import User
import json

router = APIRouter()

@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def create_novel(
    novel_data: NovelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return NovelService.create_novel(db, novel_data, current_user.id)

@router.get("/", response_model=NovelListResponse)
async def get_novels(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    genre: Optional[str] = None,
    status: Optional[str] = None,
    is_public: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    author_id = current_user.id if current_user else None
    novels = NovelService.get_novels(db, skip, limit, genre, status, is_public, author_id)
    total = NovelService._get_novel_query(db, genre, status, is_public, author_id).count()
    return {"novels": novels, "total": total, "page": skip // limit, "per_page": limit}

@router.get("/{novel_id}", response_model=NovelResponse)
async def get_novel(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    
    # Check permissions (public or author)
    if not novel.is_public and (not current_user or novel.author_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this novel")
        
    return novel

@router.put("/{novel_id}", response_model=NovelResponse)
async def update_novel(
    novel_id: int,
    novel_data: NovelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    if novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this novel")
    
    return NovelService.update_novel(db, novel_id, novel_data)

@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_novel(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    if novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this novel")
    
    if not NovelService.delete_novel(db, novel_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete novel")

@router.get("/{novel_id}/chapters", response_model=List[ChapterResponse])
async def get_novel_chapters(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Check permissions for the novel
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    
    # Check permissions (public or author)
    if not novel.is_public and (not current_user or novel.author_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this novel")
        
    return NovelService.get_novel_chapters(db, novel_id)

@router.post("/upload", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
async def upload_novel_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        file_content = await file.read()
        decoded_content = file_content.decode('utf-8')
        import_data = json.loads(decoded_content)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid file format: {e}")

    return NovelService.import_novel_from_file(db, import_data, current_user.id)

# TODO: Add publish_novel, get_novel_stats, etc. if needed later 

async def publish_novel(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    if novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to publish this novel")
    
    return NovelService.publish_novel(db, novel_id)



async def get_novel_stats(
    novel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    return NovelService.get_novel_stats(db, novel_id)




