from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from database import get_db
from schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse, ChapterListResponse
from services.chapter import ChapterService
from services.auth import get_current_user
from models_init import User
from services.novel import NovelService
from models_init import Chapter

router = APIRouter()

@router.post("/", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    chapter_data: ChapterCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the novel exists and belongs to the current user
    novel = NovelService.get_novel_by_id(db, chapter_data.novel_id)
    if not novel or novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create chapters for this novel")

    return ChapterService.create_chapter(db, chapter_data)

@router.get("/", response_model=ChapterListResponse)
async def get_chapters(
    novel_id: Optional[Union[int, str]] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_published: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    # Преобразуем novel_id в int если это возможно
    parsed_novel_id = None
    if novel_id is not None:
        try:
            parsed_novel_id = int(novel_id)
        except (ValueError, TypeError):
            # Если не удается преобразовать в int, возвращаем ошибку
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                detail=f"Invalid novel_id format: '{novel_id}'. Expected integer."
            )
    
    if parsed_novel_id:
        # If novel_id is provided, check permissions for that novel
        novel = NovelService.get_novel_by_id(db, parsed_novel_id)
        if not novel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
        if not novel.is_public and (not current_user or novel.author_id != current_user.id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access chapters for this novel")
        
    else:
        # If no novel_id, only allow access to public chapters or user's chapters
        if not current_user:
            is_published = True # Only public chapters for anonymous users

    chapters = ChapterService.get_chapters(db, parsed_novel_id, skip, limit, is_published)
    total = db.query(Chapter).filter(Chapter.novel_id == parsed_novel_id if parsed_novel_id else True).count()
    
    return {"chapters": chapters, "total": total, "page": skip // limit, "per_page": limit}

@router.get("/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    chapter = ChapterService.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    novel = NovelService.get_novel_by_id(db, chapter.novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated novel not found")

    if not novel.is_public and (not current_user or novel.author_id != current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this chapter")

    # TODO: Increment views if needed
    return chapter

@router.put("/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: int,
    chapter_data: ChapterUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = ChapterService.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    novel = NovelService.get_novel_by_id(db, chapter.novel_id)
    if not novel or novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this chapter")

    return ChapterService.update_chapter(db, chapter_id, chapter_data)

@router.delete("/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = ChapterService.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")

    novel = NovelService.get_novel_by_id(db, chapter.novel_id)
    if not novel or novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this chapter")

    if not ChapterService.delete_chapter(db, chapter_id):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete chapter")

# TODO: Add publish_chapter, reorder_chapters, get_chapter_stats, etc. if needed later 


async def publish_chapter(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = ChapterService.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    
    novel = NovelService.get_novel_by_id(db, chapter.novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated novel not found")
    if novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to publish this chapter")
    
    return ChapterService.publish_chapter(db, chapter_id)
    
    


async def reorder_chapters(
    novel_id: int,
    chapter_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    novel = NovelService.get_novel_by_id(db, novel_id)
    if not novel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Novel not found")
    if novel.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to reorder chapters for this novel")
    
    return ChapterService.reorder_chapters(db, novel_id, chapter_ids)
    
    


async def get_chapter_stats(
    chapter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    chapter = ChapterService.get_chapter_by_id(db, chapter_id)
    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chapter not found")
    return ChapterService.get_chapter_stats(db, chapter_id)


    
    