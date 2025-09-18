from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
from pydantic import BaseModel

from services.context_manager import context_manager

router = APIRouter()

class CharacterInfo(BaseModel):
    name: str
    description: str
    traits: List[str] = []

class StylePreference(BaseModel):
    tone: str = "neutral"
    pov: str = "third_person"
    tense: str = "past"
    genre: str = "general"

class SceneContext(BaseModel):
    scene_description: str

class ChapterSummary(BaseModel):
    chapter_id: int
    summary: str

@router.post("/character")
async def add_character(character: CharacterInfo):
    """Добавить информацию о персонаже."""
    context_manager.add_character(
        character.name,
        character.description,
        character.traits
    )
    return {"message": f"Персонаж {character.name} добавлен"}

@router.post("/world-info")
async def update_world_info(info: Dict[str, Any]):
    """Обновить информацию о мире истории."""
    for key, value in info.items():
        context_manager.update_world_info(key, value)
    return {"message": "Информация о мире обновлена"}

@router.post("/style")
async def set_style_preferences(style: StylePreference):
    """Установить стилевые предпочтения."""
    for key, value in style.dict().items():
        context_manager.set_style_preference(key, value)
    return {"message": "Стилевые предпочтения обновлены"}

@router.post("/scene")
async def set_current_scene(scene: SceneContext):
    """Установить контекст текущей сцены."""
    context_manager.set_current_scene(scene.scene_description)
    return {"message": "Контекст сцены обновлен"}

@router.post("/chapter-summary")
async def add_chapter_summary(summary: ChapterSummary):
    """Добавить краткое содержание главы."""
    context_manager.add_chapter_summary(summary.chapter_id, summary.summary)
    return {"message": f"Краткое содержание главы {summary.chapter_id} добавлено"}

@router.get("/export")
async def export_context():
    """Экспортировать весь контекст."""
    return {
        "context": context_manager.export_context()
    }

@router.post("/import")
async def import_context(context_data: Dict[str, Any]):
    """Импортировать контекст."""
    try:
        import json
        context_manager.import_context(json.dumps(context_data))
        return {"message": "Контекст импортирован успешно"}
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка импорта контекста: {str(e)}"
        )

@router.delete("/clear")
async def clear_context():
    """Очистить весь контекст."""
    # Создаем новый экземпляр для очистки
    context_manager.__init__()
    return {"message": "Контекст очищен"}